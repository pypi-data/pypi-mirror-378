# AIDEV-SECTION: DAEMON_CONNECTOR
"""
daemon_connector.py - PostgreSQL-friendly wrapper for SteadyText daemon communication

AIDEV-NOTE: This module provides the bridge between PostgreSQL and SteadyText's ZeroMQ daemon.
It handles automatic daemon startup, connection management, and fallback to direct generation.
"""

import json
import time
import subprocess
import logging
from typing import List, Optional, cast
import numpy as np

# AIDEV-NOTE: Import SteadyText components - these should be available if steadytext is installed
try:
    from steadytext import (
        generate,
        embed,
        rerank,
        generate_iter,
        generate_json,
        generate_regex,
        generate_choice,
    )
    from steadytext.daemon import use_daemon

    STEADYTEXT_AVAILABLE = True
except ImportError as e:
    STEADYTEXT_AVAILABLE = False
    import sys

    logging.warning(
        f"SteadyText not available - extension will use fallback mode. Error: {e}"
    )
    logging.warning(f"Python path: {sys.path}")
    logging.warning("Install SteadyText with: pip3 install steadytext")

# Configure logging
logger = logging.getLogger(__name__)


class SteadyTextConnector:
    """
    PostgreSQL-friendly wrapper for SteadyText daemon communication.

    AIDEV-NOTE: This class provides a stable interface for PostgreSQL functions
    to interact with SteadyText, handling daemon lifecycle and fallbacks.
    """

    def __init__(
        self, host: str = "localhost", port: int = 5555, auto_start: bool = True
    ):
        """
        Initialize the SteadyText connector.

        Args:
            host: Daemon host address
            port: Daemon port number
            auto_start: Whether to auto-start daemon if not running
        """
        # AIDEV-NOTE: Validate host parameter to prevent injection attacks
        if not host:
            raise ValueError("Host cannot be empty")

        # Allow alphanumeric, dots, hyphens, and underscores (for hostnames and IPs)
        import re

        if not re.match(r"^[a-zA-Z0-9._-]+$", host):
            raise ValueError(
                f"Invalid host: {host}. Only alphanumeric characters, dots, hyphens, and underscores are allowed."
            )

        # Basic IP address validation (both IPv4 and simple hostname)
        if host.count(".") > 0:  # Might be an IP
            parts = host.split(".")
            if len(parts) == 4:  # IPv4 format
                try:
                    for part in parts:
                        num = int(part)
                        if num < 0 or num > 255:
                            raise ValueError(f"Invalid IP address: {host}")
                except ValueError:
                    pass  # Not an IP, might be hostname

        # Validate port parameter
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError(
                f"Invalid port: {port}. Port must be an integer between 1 and 65535."
            )

        self.host = host
        self.port = port
        self.auto_start = auto_start
        self.daemon_endpoint = f"tcp://{host}:{port}"

        # AIDEV-NOTE: Skip daemon checks - they will be done lazily when needed
        # This avoids unnecessary model loading for remote models with unsafe_mode

    def _ensure_daemon_running(self) -> bool:
        """
        Ensure the SteadyText daemon is running, starting it if necessary.

        AIDEV-NOTE: This method tries to connect to the daemon and starts it
        if the connection fails. It uses the SteadyText CLI for daemon management.

        Returns:
            True if daemon is running or was started successfully, False otherwise
        """
        if not STEADYTEXT_AVAILABLE:
            logger.error("SteadyText not available - cannot start daemon")
            return False

        # Use the lightweight check first
        if self.is_daemon_running():
            return True

        # Daemon not running
        if self.auto_start:
            logger.info("Attempting to start SteadyText daemon...")
            return self._start_daemon()

        return False

    def _start_daemon(self) -> bool:
        """
        Start the SteadyText daemon using the CLI.

        AIDEV-NOTE: Uses subprocess to run 'st daemon start' command.
        Waits briefly for daemon to become available.

        Returns:
            True if daemon started successfully, False otherwise
        """
        try:
            # Start daemon using SteadyText CLI
            result = subprocess.run(
                [
                    "st",
                    "daemon",
                    "start",
                    "--host",
                    self.host,
                    "--port",
                    str(self.port),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.error(f"Failed to start daemon: {result.stderr}")
                return False

            # Wait for daemon to become available
            for i in range(10):  # Try for up to 5 seconds
                time.sleep(0.5)
                try:
                    with use_daemon():
                        test_result = generate("test", max_new_tokens=1)
                        if test_result:
                            logger.info("SteadyText daemon started successfully")
                            return True
                except Exception:
                    continue

            logger.error("Daemon started but not responding")
            return False

        except subprocess.TimeoutExpired:
            logger.error("Timeout starting daemon")
            return False
        except Exception as e:
            logger.error(f"Error starting daemon: {e}")
            return False

    def start_daemon(self) -> bool:
        """
        Public method to start the SteadyText daemon.

        AIDEV-NOTE: Added public wrapper for _start_daemon() to fix SQL compatibility
        issue where pg_steadytext--1.4.1.sql calls connector.start_daemon().

        Returns:
            True if daemon started successfully, False otherwise
        """
        return self._start_daemon()

    def is_daemon_running(self) -> bool:
        """
        Check if the SteadyText daemon is currently running.

        AIDEV-NOTE: This method checks if the daemon is responsive by attempting
        a simple operation. Used by worker.py to determine daemon availability.

        Returns:
            True if daemon is running and responsive, False otherwise
        """
        if not STEADYTEXT_AVAILABLE:
            return False

        try:
            # AIDEV-NOTE: First try the steadytext CLI module's daemon check
            # This function checks the PID file to see if daemon is running
            try:
                from steadytext.cli.commands.daemon import (
                    is_daemon_running as check_daemon,
                )
                from steadytext.cli.commands.daemon import get_pid_file

                return check_daemon(get_pid_file())
            except ImportError:
                pass  # Module not available, try alternative

            # AIDEV-NOTE: Fallback to checking ZMQ socket connectivity
            # This avoids model loading that happens with generate()
            import zmq

            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
            socket.setsockopt(zmq.LINGER, 0)  # Don't linger on close
            socket.setsockopt(zmq.SNDTIMEO, 1000)  # Send timeout

            try:
                socket.connect(self.daemon_endpoint)

                # Try a minimal message that daemon might respond to
                # Some daemons may not support ping/pong but will respond to invalid requests
                test_msg = {
                    "method": "status",  # Try a status request
                    "id": "test-connection",
                    "params": {},
                }
                socket.send_json(test_msg)

                # Try to receive any response
                try:
                    response = socket.recv_json()
                    # Any valid JSON response means daemon is running
                    return isinstance(response, dict)
                except zmq.Again:
                    # Timeout - daemon not responding
                    return False

            finally:
                socket.close()
                context.term()

        except Exception:
            # Any exception means daemon is not running
            return False

    def check_health(self) -> dict:
        """
        Get detailed health status of the daemon.

        AIDEV-NOTE: Returns a dictionary with health information.
        This method is referenced in the SQL file for daemon status checking.

        Returns:
            Dictionary with health status information
        """
        health_info = {
            "status": "unhealthy",
            "endpoint": self.daemon_endpoint,
            "steadytext_available": STEADYTEXT_AVAILABLE,
        }

        if self.is_daemon_running():
            health_info["status"] = "healthy"

        return health_info

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        max_new_tokens: Optional[int] = None,
        unsafe_mode: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate text using SteadyText with automatic fallback.

        AIDEV-NOTE: This method tries to use the daemon first, then falls back
        to direct generation if daemon is unavailable. This ensures the PostgreSQL
        extension always returns a result.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate (legacy parameter name)
            max_new_tokens: Maximum tokens to generate (SteadyText parameter name)
            **kwargs: Additional generation parameters

        Returns:
            Generated text string
        """
        # AIDEV-NOTE: Handle both parameter names for compatibility
        if max_new_tokens is None:
            max_new_tokens = max_tokens or 512

        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not kwargs.get("model"):
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )

        if not STEADYTEXT_AVAILABLE:
            # Return deterministic fallback if SteadyText not available
            return self._fallback_generate(prompt, max_new_tokens)

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        # Remote models don't benefit from daemon and trying to use it causes delays
        model = kwargs.get("model")
        if unsafe_mode and model and ":" in model:
            try:
                result = generate(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                # Handle both str and tuple returns
                if isinstance(result, tuple):
                    return cast(str, result[0])  # First element is always the text
                else:
                    return cast(str, result)
            except Exception as e:
                logger.error(f"Remote model generation failed: {e}")
                return self._fallback_generate(prompt, max_new_tokens)

        # For local models, try daemon first
        try:
            # Ensure daemon is running only when we actually need it
            if self.auto_start and not self.is_daemon_running():
                self._start_daemon()

            # Try using daemon first
            with use_daemon():
                result = generate(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                # Handle both str and tuple returns
                if isinstance(result, tuple):
                    return cast(str, result[0])  # First element is always the text
                else:
                    return cast(str, result)
        except Exception as e:
            logger.warning(f"Daemon generation failed: {e}, using direct generation")

            # Fall back to direct generation
            try:
                result = generate(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                # Handle both str and tuple returns
                if isinstance(result, tuple):
                    return cast(str, result[0])  # First element is always the text
                else:
                    return cast(str, result)
            except Exception as e2:
                logger.error(f"Direct generation also failed: {e2}")
                return self._fallback_generate(prompt, max_new_tokens)

    def generate_stream(
        self, prompt: str, max_tokens: int = 512, unsafe_mode: bool = False, **kwargs
    ):
        """
        Generate text in streaming mode.

        AIDEV-NOTE: Yields tokens as they are generated. Falls back to
        chunked output if streaming not available.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters

        Yields:
            Text tokens as they are generated
        """
        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not kwargs.get("model"):
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )
        if not STEADYTEXT_AVAILABLE:
            # Yield fallback in chunks
            result = self._fallback_generate(prompt, max_tokens)
            for word in result.split():
                yield word + " "
            return

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        model = kwargs.get("model")
        if unsafe_mode and model and ":" in model:
            try:
                for token in generate_iter(
                    prompt,
                    max_new_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                ):
                    yield token
            except Exception as e:
                logger.error(f"Remote model streaming failed: {e}")
                # Yield fallback in chunks
                result = self._fallback_generate(prompt, max_tokens)
                for word in result.split():
                    yield word + " "
            return

        # For local models, try daemon first
        try:
            # Ensure daemon is running only when we actually need it
            if self.auto_start and not self.is_daemon_running():
                self._start_daemon()

            # Try streaming with daemon
            with use_daemon():
                for token in generate_iter(
                    prompt,
                    max_new_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                ):
                    yield token
        except Exception as e:
            logger.warning(f"Daemon streaming failed: {e}, using direct streaming")

            # Fall back to direct streaming
            try:
                for token in generate_iter(
                    prompt,
                    max_new_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                ):
                    yield token
            except Exception as e2:
                logger.error(f"Direct streaming also failed: {e2}")
                # Yield fallback in chunks
                result = self._fallback_generate(prompt, max_tokens)
                for word in result.split():
                    yield word + " "

    def embed(
        self,
        text: str,
        seed: int = 42,
        model: Optional[str] = None,
        unsafe_mode: bool = False,
    ) -> np.ndarray:
        """
        Generate embedding for text using SteadyText with optional remote models.

        AIDEV-NOTE: Returns a 1024-dimensional normalized embedding vector.
        Falls back to zero vector if generation fails. Supports remote models
        (e.g., OpenAI) with unsafe_mode.

        Args:
            text: Input text to embed
            seed: Random seed for deterministic embeddings (default: 42)
            model: Optional remote model string (e.g., "openai:text-embedding-3-small")
            unsafe_mode: Enable remote models with best-effort determinism

        Returns:
            1024-dimensional numpy array
        """
        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not model:
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )

        if not STEADYTEXT_AVAILABLE:
            # Return zero vector as fallback
            return np.zeros(1024, dtype=np.float32)

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        # Remote models don't benefit from daemon and trying to use it causes delays
        if unsafe_mode and model and ":" in model:
            try:
                result = embed(text, seed=seed, model=model, unsafe_mode=unsafe_mode)
                if result is not None:
                    return result
                # If None, fall through to return zero vector
            except Exception as e:
                logger.error(f"Remote model embedding failed: {e}")
                # Fall through to return zero vector
        else:
            # For local models, try daemon first
            try:
                # Try using daemon first
                with use_daemon():
                    # Check if embed supports unsafe_mode parameter
                    import inspect

                    embed_sig = inspect.signature(embed)
                    kwargs = {"seed": seed}
                    if model:
                        kwargs["model"] = model
                    if unsafe_mode and "unsafe_mode" in embed_sig.parameters:
                        kwargs["unsafe_mode"] = unsafe_mode
                    result = embed(text, **kwargs)
                    if result is not None:
                        return result
                    # If None, fall through to return zero vector
            except Exception as e:
                logger.warning(f"Daemon embedding failed: {e}, using direct embedding")

                # Fall back to direct embedding
                try:
                    # Check if embed supports unsafe_mode parameter
                    import inspect

                    embed_sig = inspect.signature(embed)
                    kwargs = {"seed": seed}
                    if model:
                        kwargs["model"] = model
                    if unsafe_mode and "unsafe_mode" in embed_sig.parameters:
                        kwargs["unsafe_mode"] = unsafe_mode
                    result = embed(text, **kwargs)
                    if result is not None:
                        return result
                    # If None, fall through to return zero vector
                except Exception as e2:
                    logger.error(f"Direct embedding also failed: {e2}")

        # Return zero vector as fallback
        return np.zeros(1024, dtype=np.float32)

    def generate_json(
        self,
        prompt: str,
        schema: dict,
        max_tokens: int = 512,
        unsafe_mode: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate JSON text using schema constraints.

        AIDEV-NOTE: This method generates JSON that conforms to the provided
        schema using llama.cpp's grammar support.

        Args:
            prompt: Input text prompt
            schema: JSON schema dictionary
            max_tokens: Maximum tokens to generate
            unsafe_mode: Enable remote models (requires model parameter)
            **kwargs: Additional generation parameters (including model)

        Returns:
            JSON string that conforms to the schema
        """
        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not kwargs.get("model"):
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )
        if not STEADYTEXT_AVAILABLE:
            # Return fallback JSON
            return self._fallback_generate_json(prompt, schema, max_tokens)

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        model = kwargs.get("model")
        if unsafe_mode and model and ":" in model:
            try:
                result = generate_json(
                    prompt,
                    schema=schema,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e:
                logger.error(f"Remote model JSON generation failed: {e}")
                return self._fallback_generate_json(prompt, schema, max_tokens)

        # For local models, try daemon first
        try:
            # Try using daemon first
            with use_daemon():
                result = generate_json(
                    prompt,
                    schema=schema,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
        except Exception as e:
            logger.warning(
                f"Daemon JSON generation failed: {e}, using direct generation"
            )

            # Fall back to direct generation
            try:
                result = generate_json(
                    prompt,
                    schema=schema,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e2:
                logger.error(f"Direct JSON generation also failed: {e2}")
                return self._fallback_generate_json(prompt, schema, max_tokens)

    def generate_regex(
        self,
        prompt: str,
        pattern: str,
        max_tokens: int = 512,
        unsafe_mode: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate text that matches a regex pattern.

        AIDEV-NOTE: This method generates text constrained by the provided
        regex pattern using llama.cpp's grammar support.

        Args:
            prompt: Input text prompt
            pattern: Regular expression pattern
            max_tokens: Maximum tokens to generate
            unsafe_mode: Enable remote models (requires model parameter)
            **kwargs: Additional generation parameters (including model)

        Returns:
            Text that matches the pattern
        """
        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not kwargs.get("model"):
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )
        if not STEADYTEXT_AVAILABLE:
            # Return simple fallback
            return self._fallback_generate(prompt, max_tokens)

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        model = kwargs.get("model")
        if unsafe_mode and model and ":" in model:
            try:
                result = generate_regex(
                    prompt,
                    pattern=pattern,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e:
                logger.error(f"Remote model regex generation failed: {e}")
                return self._fallback_generate(prompt, max_tokens)

        # For local models, try daemon first
        try:
            # Try using daemon first
            with use_daemon():
                result = generate_regex(
                    prompt,
                    pattern=pattern,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
        except Exception as e:
            logger.warning(
                f"Daemon regex generation failed: {e}, using direct generation"
            )

            # Fall back to direct generation
            try:
                result = generate_regex(
                    prompt,
                    pattern=pattern,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e2:
                logger.error(f"Direct regex generation also failed: {e2}")
                return self._fallback_generate(prompt, max_tokens)

    def generate_choice(
        self,
        prompt: str,
        choices: List[str],
        max_tokens: int = 512,
        unsafe_mode: bool = False,
        **kwargs,
    ) -> str:
        """
        Generate text that is one of the provided choices.

        AIDEV-NOTE: This method generates text constrained to one of the
        provided choices using llama.cpp's grammar support.

        Args:
            prompt: Input text prompt
            choices: List of allowed string choices
            max_tokens: Maximum tokens to generate
            unsafe_mode: Enable remote models (requires model parameter)
            **kwargs: Additional generation parameters (including model)

        Returns:
            One of the provided choices
        """
        # AIDEV-NOTE: Validate that unsafe_mode requires a model to be specified
        if unsafe_mode and not kwargs.get("model"):
            raise ValueError(
                "unsafe_mode=True requires a model parameter to be specified"
            )
        if not STEADYTEXT_AVAILABLE:
            # Return deterministic choice
            return choices[abs(hash(prompt)) % len(choices)] if choices else ""

        # AIDEV-NOTE: For remote models with unsafe_mode, skip daemon entirely
        model = kwargs.get("model")
        if unsafe_mode and model and ":" in model:
            try:
                result = generate_choice(
                    prompt,
                    choices=choices,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e:
                logger.error(f"Remote model choice generation failed: {e}")
                # Return deterministic choice
                return choices[abs(hash(prompt)) % len(choices)] if choices else ""

        # For local models, try daemon first
        try:
            # Try using daemon first
            with use_daemon():
                result = generate_choice(
                    prompt,
                    choices=choices,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
        except Exception as e:
            logger.warning(
                f"Daemon choice generation failed: {e}, using direct generation"
            )

            # Fall back to direct generation
            try:
                result = generate_choice(
                    prompt,
                    choices=choices,
                    max_tokens=max_tokens,
                    unsafe_mode=unsafe_mode,
                    **kwargs,
                )
                return cast(str, result)
            except Exception as e2:
                logger.error(f"Direct choice generation also failed: {e2}")
                # Return deterministic choice
                return choices[abs(hash(prompt)) % len(choices)] if choices else ""

    def rerank(
        self,
        query: str,
        documents: List[str],
        task: str = "Given a web search query, retrieve relevant passages that answer the query",
        return_scores: bool = True,
        seed: int = 42,
    ) -> List:
        """
        Rerank documents by relevance to a query using SteadyText.

        AIDEV-NOTE: Uses the Qwen3-Reranker model to score query-document pairs.
        Falls back to simple word overlap scoring if model unavailable.

        Args:
            query: Search query text
            documents: List of documents to rerank
            task: Task description for reranking
            return_scores: If True, return (document, score) tuples; if False, just documents
            seed: Random seed for deterministic reranking (default: 42)

        Returns:
            List of (document, score) tuples if return_scores=True,
            otherwise list of documents sorted by relevance
        """
        if not documents:
            return []

        if not STEADYTEXT_AVAILABLE:
            # Fallback reranking using simple word overlap
            return self._fallback_rerank(query, documents, return_scores)

        try:
            # Try using daemon first
            with use_daemon():
                result = rerank(
                    query=query,
                    documents=documents,
                    task=task,
                    return_scores=return_scores,
                    seed=seed,
                )
                return result
        except Exception as e:
            logger.warning(f"Daemon reranking failed: {e}, using direct reranking")

            # Fall back to direct reranking
            try:
                result = rerank(
                    query=query,
                    documents=documents,
                    task=task,
                    return_scores=return_scores,
                    seed=seed,
                )
                return result
            except Exception as e2:
                logger.error(f"Direct reranking also failed: {e2}")
                return self._fallback_rerank(query, documents, return_scores)

    def _fallback_rerank(
        self, query: str, documents: List[str], return_scores: bool
    ) -> List:
        """
        Fallback reranking using simple word overlap scoring.

        AIDEV-NOTE: Provides deterministic reranking when model is unavailable.
        """
        query_words = set(query.lower().split())

        # Score each document
        scored_docs = []
        for doc in documents:
            doc_words = set(doc.lower().split())
            if query_words:
                overlap = len(query_words.intersection(doc_words))
                score = overlap / len(query_words)
            else:
                score = 0.0
            scored_docs.append((doc, score))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        if return_scores:
            return scored_docs
        else:
            return [doc for doc, _ in scored_docs]

    def _fallback_generate(self, prompt: str, max_tokens: int) -> str:
        """
        Deterministic fallback text generation.

        AIDEV-NOTE: This provides a predictable output when SteadyText
        is unavailable, ensuring the PostgreSQL extension never errors.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens (used to limit output)

        Returns:
            Deterministic text based on prompt
        """
        # Use hash of prompt for deterministic output
        hash_val = abs(hash(prompt)) % 1000

        templates = [
            f"Generated response for prompt (hash: {hash_val}): {prompt[:50]}...",
            f"SteadyText fallback output #{hash_val} for input: {prompt[:50]}...",
            f"Deterministic response {hash_val}: Processing '{prompt[:50]}...'",
        ]

        # Select template based on hash
        template = templates[hash_val % len(templates)]

        # Limit to approximate token count (assuming ~4 chars per token)
        max_chars = max_tokens * 4
        return template[:max_chars]

    def _fallback_generate_json(
        self, prompt: str, schema: dict, max_tokens: int
    ) -> str:
        """
        Deterministic fallback JSON generation.

        AIDEV-NOTE: This provides a predictable JSON output when SteadyText
        is unavailable.

        Args:
            prompt: Input prompt
            schema: JSON schema (used to create basic structure)
            max_tokens: Maximum tokens (ignored for JSON)

        Returns:
            Deterministic JSON based on schema
        """
        # Create a simple JSON object based on schema
        result = {}
        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                prop_type = prop_schema.get("type", "string")
                if prop_type == "string":
                    result[prop] = f"fallback_{prop}"
                elif prop_type == "integer":
                    result[prop] = abs(hash(prompt + prop)) % 100
                elif prop_type == "boolean":
                    result[prop] = (abs(hash(prompt + prop)) % 2) == 0
                elif prop_type == "number":
                    result[prop] = (abs(hash(prompt + prop)) % 100) / 10.0
                elif prop_type == "array":
                    result[prop] = []
                elif prop_type == "object":
                    result[prop] = {}

        return json.dumps(result)


# AIDEV-NOTE: Module-level convenience functions for PostgreSQL integration
_default_connector: Optional[SteadyTextConnector] = None


def get_default_connector() -> SteadyTextConnector:
    """Get or create the default connector instance."""
    global _default_connector
    if _default_connector is None:
        _default_connector = SteadyTextConnector()
    assert _default_connector is not None
    return cast(SteadyTextConnector, _default_connector)


def pg_generate(prompt: str, max_tokens: int = 512, **kwargs) -> str:
    """PostgreSQL-friendly wrapper for text generation."""
    connector = get_default_connector()
    return connector.generate(prompt, max_tokens, **kwargs)


def pg_embed(
    text: str, seed: int = 42, model: Optional[str] = None, unsafe_mode: bool = False
) -> List[float]:
    """PostgreSQL-friendly wrapper for embedding generation with remote model support."""
    connector = get_default_connector()
    embedding = connector.embed(text, seed=seed, model=model, unsafe_mode=unsafe_mode)
    return embedding.tolist()  # Convert to list for PostgreSQL


def pg_generate_json(prompt: str, schema: dict, max_tokens: int = 512, **kwargs) -> str:
    """PostgreSQL-friendly wrapper for JSON generation."""
    connector = get_default_connector()
    return connector.generate_json(prompt, schema, max_tokens, **kwargs)


def pg_generate_regex(
    prompt: str, pattern: str, max_tokens: int = 512, **kwargs
) -> str:
    """PostgreSQL-friendly wrapper for regex-constrained generation."""
    connector = get_default_connector()
    return connector.generate_regex(prompt, pattern, max_tokens, **kwargs)


def pg_generate_choice(
    prompt: str, choices: List[str], max_tokens: int = 512, **kwargs
) -> str:
    """PostgreSQL-friendly wrapper for choice-constrained generation."""
    connector = get_default_connector()
    return connector.generate_choice(prompt, choices, max_tokens, **kwargs)
