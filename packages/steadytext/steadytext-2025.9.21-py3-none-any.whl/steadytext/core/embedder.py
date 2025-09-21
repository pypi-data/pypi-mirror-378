# AIDEV-ANCHOR: embedder: L2 normalized vectors
# AIDEV-NOTE: L2 normalization, zero fallback, batch averaging, remote provider support

import logging
import os
from typing import (
    List,
    Optional,
    Union,
)

import numpy as np

try:
    from llama_cpp import Llama  # type: ignore
except ImportError as import_err:  # pragma: no cover - allow missing llama_cpp
    Llama = None  # type: ignore
    logging.getLogger(__name__).error("llama_cpp not available: %s", import_err)

from ..cache_manager import get_embedding_cache
from ..models.loader import (
    get_embedding_model_instance,
)
from ..utils import (
    EMBEDDING_DIMENSION,
    JINA_V4_FULL_DIMENSION,
    logger,
    validate_normalized_embedding,
    DEFAULT_SEED,
    validate_seed,
    get_default_embedding_mode,
)

# AIDEV-NOTE: Use centralized cache manager for consistent caching.
# AIDEV-NOTE: Zero-vector fallbacks for invalid inputs are NOT cached by design to ensure data quality issues remain visible.


# AIDEV-NOTE: L2 normalization is crucial for consistent vector similarity calculations. It handles near-zero vectors to prevent division by zero.
def _normalize_l2(vector: np.ndarray, tolerance: float = 1e-9) -> np.ndarray:
    """
    L2 normalizes a numpy vector.
    If the norm is very close to zero (e.g., a zero vector from an error),
    returns the vector as is (which will be a zero vector of the correct dtype).
    Ensures output is float32.
    """
    norm = np.linalg.norm(vector)
    if norm < tolerance:  # Effectively a zero vector
        # logger.debug("Embedding norm is close to zero. Returning as-is (zero vector, float32).")
        return vector.astype(np.float32)
    normalized_vector = (vector / norm).astype(np.float32)
    return normalized_vector


# AIDEV-NOTE: Main embedding function with comprehensive error handling and fallback
# Supports both string and list inputs with proper dimension validation
# Now supports remote models with unsafe_mode parameter
def core_embed(
    text_input: Union[str, List[str]],
    seed: int = DEFAULT_SEED,
    model: Optional[str] = None,
    unsafe_mode: bool = False,
    mode: Optional[str] = None,
) -> np.ndarray:
    """
    Creates a fixed-dimension, L2-normalized embedding for the input text(s)
    using the pre-loaded GGUF model configured for embeddings or remote providers.

    Args:
        text_input (Union[str, List[str]]): The input text or a list of texts to embed.
            - If a single string, it's embedded directly.
            - If a list of strings, embeddings for each non-empty string
              are computed and then averaged to produce a single embedding vector.
            - Empty strings, empty lists, or lists with only empty/whitespace
              strings will result in a zero vector of EMBEDDING_DIMENSION.
        seed: Seed for deterministic behavior (ignored by most remote providers)
        model: Optional remote model string (e.g., "openai:text-embedding-3-small")
        unsafe_mode: Enable remote models with best-effort determinism
        mode: Optional embedding mode ("query" or "passage") for Jina v4 models

    Returns:
        numpy.ndarray: A 1D numpy array of shape (EMBEDDING_DIMENSION,)
                       and dtype float32, representing the L2-normalized
                       embedding. Returns a zero vector on errors or
                       for invalid/empty inputs.

    Raises:
        TypeError: If input is not a string or list of strings (intended to be caught
                   by the public API layer for a "Never Fails" zero vector response).
    """
    validate_seed(seed)

    # AIDEV-NOTE: Determine embedding mode (query or passage) for Jina v4
    if mode is None:
        mode = get_default_embedding_mode()
    elif mode.lower() not in ["query", "passage"]:
        logger.warning(f"Invalid embedding mode '{mode}', using 'query'")
        mode = "query"
    else:
        mode = mode.lower()

    # AIDEV-NOTE: Check for remote models first
    if model:
        from ..providers.registry import is_remote_model, get_provider

        if is_remote_model(model):
            # AIDEV-NOTE: Temporarily enable unsafe mode for this call if requested
            old_unsafe_mode = os.environ.get("STEADYTEXT_UNSAFE_MODE")
            if unsafe_mode:
                os.environ["STEADYTEXT_UNSAFE_MODE"] = "true"

            try:
                provider = get_provider(model)

                # Check if provider supports embeddings
                if not provider.supports_embeddings():
                    logger.error(f"Provider for {model} does not support embeddings")
                    return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

                # Generate embedding using remote provider
                embedding = provider.embed(text_input, seed=seed)

                if embedding is None:
                    logger.error(f"Remote embedding generation failed for {model}")
                    return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

                # Ensure it's the right shape and normalized
                if embedding.shape != (EMBEDDING_DIMENSION,):
                    # Some providers may return different dimensions
                    # For now, we'll pad or truncate to match EMBEDDING_DIMENSION
                    logger.warning(
                        f"Remote embedding has dimension {embedding.shape[0]}, "
                        f"expected {EMBEDDING_DIMENSION}. Adjusting..."
                    )
                    if embedding.shape[0] < EMBEDDING_DIMENSION:
                        # Pad with zeros
                        padding = np.zeros(
                            EMBEDDING_DIMENSION - embedding.shape[0], dtype=np.float32
                        )
                        embedding = np.concatenate([embedding, padding])
                    else:
                        # Truncate
                        embedding = embedding[:EMBEDDING_DIMENSION]

                # Normalize the embedding
                normalized_embedding = _normalize_l2(embedding)

                # Cache the result
                if isinstance(text_input, str):
                    cache_key = (text_input,)
                else:
                    cache_key = tuple(text_input)
                get_embedding_cache().set(cache_key, normalized_embedding)

                return normalized_embedding

            except Exception as e:
                logger.error(f"Remote embedding generation failed: {e}")
                return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
            finally:
                # AIDEV-NOTE: Restore original unsafe mode state
                if unsafe_mode:
                    if old_unsafe_mode is None:
                        os.environ.pop("STEADYTEXT_UNSAFE_MODE", None)
                    else:
                        os.environ["STEADYTEXT_UNSAFE_MODE"] = old_unsafe_mode

    if not isinstance(text_input, (str, list)):
        logger.error(
            f"Core.embedder: Input must be str or list, got {type(text_input)}."
        )
        raise TypeError(
            f"Input text must be a string or list of strings, got {type(text_input)}"
        )

    # Prepare texts for embedding
    texts_to_embed: List[str] = []
    if isinstance(text_input, str):
        if text_input.strip():  # Not empty or just whitespace
            texts_to_embed.append(text_input)
    elif isinstance(text_input, list):
        for item in text_input:
            if not isinstance(item, str):
                logger.error(
                    f"Core.embedder: List items must be str, got {type(item)}."
                )
                raise TypeError("If input is a list, all items must be strings.")
            if item.strip():  # Not empty or just whitespace
                texts_to_embed.append(item)

    # AIDEV-NOTE: Include mode in cache key for Jina v4 to distinguish query vs passage embeddings
    # Include model identity to avoid cross-model cache collisions
    model_identity = (
        getattr(model, "model_path", None)
        or getattr(model, "model_id", None)
        or "local-embedder"
    )
    cache_key = (model_identity, mode) + tuple(texts_to_embed)

    if not texts_to_embed:
        logger.error(
            "Core.embedder: No valid non-empty text provided for embedding. "
            "Cannot create embedding from empty input."
        )
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

    cached = get_embedding_cache().get(cache_key)
    if cached is not None:
        return cached

    # AIDEV-NOTE: This is a key error handling point for model loading.
    try:
        # get_embedding_model_instance handles loading, caching, and
        # dimension validation. It will return None if model loading fails
        # or dimension is incorrect.
        model: Optional[Llama] = get_embedding_model_instance()
        if model is None:
            logger.error("Core.embedder: Could not load/get embedding model")
            return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
    except Exception as e:
        logger.error(
            f"Core.embedder: Could not load/get embedding model: {e}", exc_info=True
        )
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

    logger.debug(
        f"Core.embedder: Creating embedding for {len(texts_to_embed)} text(s)."
    )

    try:
        all_sequence_level_embeddings: List[np.ndarray] = []
        for text_item in texts_to_embed:  # non-empty strings
            # AIDEV-NOTE: Add Query/Passage prefix for Jina v4 models
            # The prefix is capitalized and followed by a colon and space
            prefixed_text = f"{mode.capitalize()}: {text_item}"

            # AIDEV-NOTE: Wrap embed call with output suppression to prevent llama.cpp warnings
            # from polluting stdout (e.g., "init: embeddings required..." warnings)
            from ..utils import suppress_llama_output

            with suppress_llama_output():
                token_embeddings_output = model.embed(
                    prefixed_text
                )  # Might be List[List[float]] or List[float]

            if not token_embeddings_output:
                logger.warning(
                    f"Core.embedder: model.embed() returned empty list for "
                    f"'{text_item[:50]}...'. Skipping."
                )
                continue

            # Ensure we have a numpy array to check dimensions
            token_embeddings_np = np.array(token_embeddings_output, dtype=np.float32)

            sequence_embedding_1d: Optional[np.ndarray] = None
            # AIDEV-NOTE: Complex dimension handling for different model output formats
            if token_embeddings_np.ndim == 2:  # Expected case: (n_tokens, n_embd)
                if token_embeddings_np.shape[0] == 0:  # No tokens produced embeddings
                    logger.warning(
                        f"Core.embedder: model.embed() for '{text_item[:50]}...' "
                        f"result in zero token embeddings. Skipping."
                    )
                    continue
                # AIDEV-NOTE: Handle Jina v4 Matryoshka truncation
                # Jina v4 outputs 2048 dimensions, we truncate to 1024
                if token_embeddings_np.shape[1] == JINA_V4_FULL_DIMENSION:
                    # Truncate to EMBEDDING_DIMENSION (1024)
                    token_embeddings_np = token_embeddings_np[:, :EMBEDDING_DIMENSION]
                    logger.debug(
                        f"Core.embedder: Truncated Jina v4 embedding from {JINA_V4_FULL_DIMENSION} "
                        f"to {EMBEDDING_DIMENSION} dimensions using Matryoshka"
                    )
                elif token_embeddings_np.shape[1] != EMBEDDING_DIMENSION:
                    logger.warning(
                        f"Core.embedder: Token embeddings for '{text_item[:50]}...' "
                        f"have unexpected dimension {token_embeddings_np.shape[1]} "
                        f"(expected {EMBEDDING_DIMENSION} or {JINA_V4_FULL_DIMENSION}). Skipping."
                    )
                    continue
                sequence_embedding_1d = np.mean(token_embeddings_np, axis=0)
            elif (
                token_embeddings_np.ndim == 1
            ):  # Case: model.embed() already returned a 1D sequence embedding
                # AIDEV-NOTE: Handle Jina v4 Matryoshka truncation for 1D case
                if token_embeddings_np.shape[0] == JINA_V4_FULL_DIMENSION:
                    # Truncate to EMBEDDING_DIMENSION (1024)
                    token_embeddings_np = token_embeddings_np[:EMBEDDING_DIMENSION]
                    logger.debug(
                        f"Core.embedder: Truncated 1D Jina v4 embedding from {JINA_V4_FULL_DIMENSION} "
                        f"to {EMBEDDING_DIMENSION} dimensions using Matryoshka"
                    )
                elif token_embeddings_np.shape[0] != EMBEDDING_DIMENSION:
                    logger.warning(
                        f"Core.embedder: 1D embedding for '{text_item[:50]}...' "
                        f"has unexpected dimension {token_embeddings_np.shape[0]} "
                        f"(expected {EMBEDDING_DIMENSION}). Skipping."
                    )
                    continue
                sequence_embedding_1d = token_embeddings_np
            else:
                logger.warning(
                    f"Core.embedder: model.embed() for '{text_item[:50]}...' "
                    f"returned array with unexpected ndim {token_embeddings_np.ndim}. "
                    f"Shape: {token_embeddings_np.shape}. Skipping."
                )
                continue

            if sequence_embedding_1d is not None:
                all_sequence_level_embeddings.append(sequence_embedding_1d)

        if not all_sequence_level_embeddings:
            logger.error(
                "Core.embedder: No valid sequence embeddings could be generated "
                "for any input text. Returning zero vector."
            )
            return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

        # Average if multiple valid sequence embeddings were generated (from a
        # list input)
        if len(all_sequence_level_embeddings) == 1:
            final_raw_embedding = all_sequence_level_embeddings[0]
        else:
            # Ensure all items are 1D arrays of the same shape before stacking.
            # This should be guaranteed if sequence_embedding_1d was formed
            # correctly.
            final_raw_embedding = np.mean(
                np.stack(all_sequence_level_embeddings), axis=0
            ).astype(np.float32)
            logger.debug(
                f"Core.embedder: Averaged {len(all_sequence_level_embeddings)} "
                f"sequence embeddings."
            )

    except Exception as e:  # Catch Llama.embed() or numpy errors
        logger.error(
            f"Core.embedder: Error during embedding generation or averaging: "
            f"{type(e).__name__} - {e}",
            exc_info=True,
        )
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
    # AIDEV-NOTE: This is an important validation step for the final embedding shape.
    # Ensure correct output shape, even if something unexpected happened.
    if final_raw_embedding.shape != (EMBEDDING_DIMENSION,):
        logger.error(
            f"Core.embedder: Generated embedding has incorrect shape: "
            f"{final_raw_embedding.shape}. Expected: ({EMBEDDING_DIMENSION},). "
            f"Returning zero vector."
        )
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

    # Normalize the final embedding (L2 norm)
    normalized_embedding = _normalize_l2(final_raw_embedding)
    get_embedding_cache().set(cache_key, normalized_embedding)

    # Final validation of the output vector (shape, dtype, norm)
    if not validate_normalized_embedding(normalized_embedding, dim=EMBEDDING_DIMENSION):
        logger.error(
            "Core.embedder: Output embedding failed validation (shape, dtype, "
            "or norm). This should ideally not happen if logic is correct. "
            "Returning zero vector."
        )
        if np.any(normalized_embedding):  # Avoid re-creating if already zero
            return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)

    # logger.debug(f"Core.embedder: Embedding created successfully. Final norm: {np.linalg.norm(normalized_embedding):.4f}")
    return normalized_embedding


if __name__ == "__main__":
    # Set logger to DEBUG for detailed output during this specific test run.
    logger.setLevel(logging.DEBUG)
    # Assuming other loggers might exist from other modules if they
    # were imported, set them too.
    for log_name in [
        "steadytext.utils",
        "steadytext.models.cache",
        "steadytext.models.loader",
    ]:
        logging.getLogger(log_name).setLevel(logging.DEBUG)

    print("--- Running Core Embedder Direct Test (downloads models if not cached) ---")

    test_cases = [
        ("A single test sentence.", "Single string"),
        (
            ["First sentence.", "Second sentence for averaging."],  # noqa E501
            "List of strings",
        ),
        (["Sentence A.", "Sentence B.", "And sentence C, a third one."], "Longer list"),
        (" ", "Whitespace string"),  # Should be zero vec
        [""],  # List containing one empty string
        ["   ", "\t"],  # List of whitespace strings
        [],  # Empty list
        ["One valid sentence", "", "Another one", "  "],  # Mixed
    ]

    for i, test_case in enumerate(test_cases):
        if isinstance(test_case, tuple):
            input_val, desc = test_case
        else:
            input_val = test_case
            desc = "No description"
        print(f"\n--- Test Case {i + 1}: {desc} ---")
        print(f"Input: {str(input_val)[:70]}")
        embedding_output = core_embed(input_val)
        norm = np.linalg.norm(embedding_output)
        print(
            f"  Output Embedding Shape: {embedding_output.shape}, "
            f"Dtype: {embedding_output.dtype}, Norm: {norm:.4f}"
        )
        is_valid = validate_normalized_embedding(embedding_output)
        print(
            f"  Output Validated by "
            f"steadytext.utils.validate_normalized_embedding: {is_valid}"
        )
        if np.all(embedding_output == 0):
            print(f"  Output is a zero vector (Norm: {norm:.4f})")
        elif not is_valid:
            print("  WARNING: Output embedding is NOT valid despite checks!")

    print("\n--- Test Type Errors for Embedder ---")
    try:
        core_embed(123)  # type: ignore
    except TypeError as e:
        print(f"SUCCESS: Caught expected TypeError for invalid input type: {e}")

    try:
        core_embed(["valid", 123, "string"])  # type: ignore
    except TypeError as e:
        print(f"SUCCESS: Caught expected TypeError for list with invalid item: {e}")

    print("\n--- Test Determinism for Embedder ---")
    text_for_determinism = (
        "This specific sentence is for testing determinism of embeddings."
    )
    emb1 = core_embed(text_for_determinism)
    emb2 = core_embed(text_for_determinism)
    if np.array_equal(emb1, emb2):
        print("SUCCESS: Embedding is deterministic for the same string input.")
    else:
        print("FAILURE: Embedding is NOT deterministic for the same string input.")
        print(f"  Norm of diff: {np.linalg.norm(emb1 - emb2)}")

    logger.info("--- Core Embedder Direct Test Finished ---")
