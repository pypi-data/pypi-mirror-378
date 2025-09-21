-- pg_steadytext--1.4.3.sql
-- Complete schema for pg_steadytext extension version 1.4.3

-- AIDEV-SECTION: CORE_TABLE_DEFINITIONS
-- Cache table that mirrors and extends SteadyText's SQLite cache
CREATE TABLE IF NOT EXISTS steadytext_cache (
    id SERIAL PRIMARY KEY,
    cache_key TEXT UNIQUE NOT NULL,  -- Matches SteadyText's cache key generation
    prompt TEXT NOT NULL,
    response TEXT,
    embedding vector(1024),  -- For embedding cache using pgvector

    -- Frecency statistics (synced with SteadyText's cache)
    access_count INT DEFAULT 1,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- SteadyText integration metadata
    steadytext_cache_hit BOOLEAN DEFAULT FALSE,  -- Whether this came from ST's cache
    model_name TEXT NOT NULL DEFAULT 'qwen3-1.7b',  -- Model used (supports switching)
    model_size TEXT CHECK (model_size IN ('small', 'medium', 'large')),
    seed INTEGER DEFAULT 42,  -- Seed used for generation
    eos_string TEXT,  -- Custom end-of-sequence string if used

    -- Generation parameters
    generation_params JSONB,  -- temperature, max_tokens, seed, etc.
    response_size INT,
    generation_time_ms INT  -- Time taken to generate (if not cached)

    -- AIDEV-NOTE: frecency_score removed - calculated via view instead
    -- Previously used GENERATED column with NOW() which is not immutable
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_steadytext_cache_key ON steadytext_cache USING hash(cache_key);
CREATE INDEX IF NOT EXISTS idx_steadytext_cache_last_accessed ON steadytext_cache(last_accessed);
CREATE INDEX IF NOT EXISTS idx_steadytext_cache_access_count ON steadytext_cache(access_count);

-- Request queue for async operations with priority and resource management
CREATE TABLE IF NOT EXISTS steadytext_queue (
    id SERIAL PRIMARY KEY,
    request_id UUID DEFAULT gen_random_uuid(),
    request_type TEXT CHECK (request_type IN ('generate', 'embed', 'batch_embed', 'rerank', 'batch_rerank')),

    -- Request data
    prompt TEXT,  -- For single requests
    prompts TEXT[],  -- For batch requests
    params JSONB,  -- Model params, seed, etc.

    -- Priority and scheduling
    priority INT DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    user_id TEXT,  -- For rate limiting per user
    session_id TEXT,  -- For request grouping

    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    result TEXT,
    results TEXT[],  -- For batch results
    embedding vector(1024),
    embeddings vector(1024)[],  -- For batch embeddings
    error TEXT,

    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    processing_time_ms INT,

    -- Resource tracking
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    daemon_endpoint TEXT  -- Which daemon instance handled this
);

CREATE INDEX IF NOT EXISTS idx_steadytext_queue_status_priority_created ON steadytext_queue(status, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_steadytext_queue_request_id ON steadytext_queue(request_id);
CREATE INDEX IF NOT EXISTS idx_steadytext_queue_user_created ON steadytext_queue(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_steadytext_queue_session ON steadytext_queue(session_id);

-- Configuration storage
CREATE TABLE IF NOT EXISTS steadytext_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT current_user
);

-- Insert default configuration
INSERT INTO steadytext_config (key, value, description) VALUES
    ('daemon_host', '"localhost"', 'SteadyText daemon host'),
    ('daemon_port', '5555', 'SteadyText daemon port'),
    ('cache_enabled', 'true', 'Enable caching'),
    ('max_cache_entries', '1000', 'Maximum cache entries'),
    ('max_cache_size_mb', '500', 'Maximum cache size in MB'),
    ('default_max_tokens', '512', 'Default max tokens for generation'),
    ('default_seed', '42', 'Default seed for deterministic generation'),
    ('daemon_auto_start', 'true', 'Auto-start daemon if not running')
    ON CONFLICT (key) DO NOTHING;

-- Daemon health monitoring
CREATE TABLE IF NOT EXISTS steadytext_daemon_health (
    daemon_id TEXT PRIMARY KEY DEFAULT 'default',
    endpoint TEXT NOT NULL,
    last_heartbeat TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'unknown' CHECK (status IN ('healthy', 'unhealthy', 'starting', 'stopping', 'unknown')),
    version TEXT,
    models_loaded TEXT[],
    memory_usage_mb INT,
    active_connections INT DEFAULT 0,
    total_requests BIGINT DEFAULT 0,
    error_count INT DEFAULT 0,
    avg_response_time_ms INT
);

-- Insert default daemon entry
INSERT INTO steadytext_daemon_health (daemon_id, endpoint, status)
VALUES ('default', 'tcp://localhost:5555', 'unknown')
ON CONFLICT (daemon_id) DO NOTHING;

-- Rate limiting per user
CREATE TABLE IF NOT EXISTS steadytext_rate_limits (
    user_id TEXT PRIMARY KEY,
    requests_per_minute INT DEFAULT 60,
    requests_per_hour INT DEFAULT 1000,
    requests_per_day INT DEFAULT 10000,
    current_minute_count INT DEFAULT 0,
    current_hour_count INT DEFAULT 0,
    current_day_count INT DEFAULT 0,
    last_reset_minute TIMESTAMPTZ DEFAULT NOW(),
    last_reset_hour TIMESTAMPTZ DEFAULT NOW(),
    last_reset_day TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log for security and debugging
CREATE TABLE IF NOT EXISTS steadytext_audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT DEFAULT current_user,
    action TEXT NOT NULL,
    request_id UUID,
    details JSONB,
    ip_address INET,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_steadytext_audit_timestamp ON steadytext_audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_steadytext_audit_user ON steadytext_audit_log(user_id, timestamp DESC);

-- AIDEV-SECTION: VIEWS
-- View for calculating frecency scores dynamically
CREATE OR REPLACE VIEW steadytext_cache_with_frecency AS
SELECT *,
    -- Calculate frecency score dynamically
    access_count * exp(-extract(epoch from (NOW() - last_accessed)) / 86400.0) AS frecency_score
FROM steadytext_cache;

-- AIDEV-NOTE: This view replaces the GENERATED column which couldn't use NOW()
-- The frecency score decays exponentially based on time since last access

-- AIDEV-SECTION: PYTHON_INTEGRATION
-- AIDEV-NOTE: Python integration layer path setup
-- This is now handled by the _steadytext_init_python function instead

-- Create Python function container
CREATE OR REPLACE FUNCTION _steadytext_init_python()
RETURNS void
LANGUAGE plpython3u
AS $c$
# AIDEV-NOTE: Initialize Python environment for pg_steadytext with enhanced error handling
import sys
import os
import site

# Get PostgreSQL lib directory with fallback
try:
    result = plpy.execute("SELECT setting FROM pg_settings WHERE name = 'pkglibdir'")
    if result and len(result) > 0 and result[0]['setting']:
        pg_lib_dir = result[0]['setting']
    else:
        # Fallback for Docker/Debian PostgreSQL 17
        pg_lib_dir = '/usr/lib/postgresql/17/lib'
        plpy.notice(f"Using fallback pkglibdir: {pg_lib_dir}")
except Exception as e:
    # Fallback for Docker/Debian PostgreSQL 17
    pg_lib_dir = '/usr/lib/postgresql/17/lib'
    plpy.notice(f"Error getting pkglibdir, using fallback: {pg_lib_dir}")

python_module_dir = os.path.join(pg_lib_dir, 'pg_steadytext', 'python')

# Save pg_lib_dir in GD for use in error messages
GD['pg_lib_dir'] = pg_lib_dir

# Verify the directory exists
if not os.path.exists(python_module_dir):
    plpy.error(f"Python module directory not found: {python_module_dir}")

# Add to Python path if not already there
if python_module_dir not in sys.path:
    sys.path.insert(0, python_module_dir)
    site.addsitedir(python_module_dir)  # Process .pth files if any

# AIDEV-NOTE: Add site-packages directory for locally installed Python packages
site_packages_dir = os.path.join(pg_lib_dir, 'pg_steadytext', 'site-packages')
if os.path.exists(site_packages_dir) and site_packages_dir not in sys.path:
    sys.path.insert(0, site_packages_dir)
    site.addsitedir(site_packages_dir)
    plpy.notice(f"Added site-packages to path: {site_packages_dir}")

# AIDEV-NOTE: Add common Python package locations
# These are common locations where pip might install packages
common_paths = [
    # User site-packages
    site.getusersitepackages(),
    # System-wide site-packages
    '/usr/local/lib/python3.10/dist-packages',
    '/usr/local/lib/python3.11/dist-packages',
    '/usr/local/lib/python3.12/dist-packages',
    '/usr/lib/python3/dist-packages',
    # Virtual environment (if activated)
    os.path.join(sys.prefix, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages'),
]

for path in common_paths:
    if path and os.path.exists(path) and path not in sys.path:
        sys.path.append(path)

# Log Python path for debugging
plpy.notice(f"Python path: {sys.path}")
plpy.notice(f"Looking for modules in: {python_module_dir}")

# Check if directory exists
if not os.path.exists(python_module_dir):
    plpy.error(f"Python module directory does not exist: {python_module_dir}")

# List files in directory for debugging
try:
    files = os.listdir(python_module_dir)
    plpy.notice(f"Files in module directory: {files}")
except Exception as e:
    plpy.warning(f"Could not list module directory: {e}")

# Try to import required external packages first
required_packages = {
    'steadytext': 'SteadyText library',
    'zmq': 'ZeroMQ for daemon communication',
    'numpy': 'NumPy for embeddings'
}

missing_packages = []
for package, description in required_packages.items():
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(f"{package} ({description})")

if missing_packages:
    pg_lib_dir = GD.get('pg_lib_dir', '/usr/lib/postgresql/17/lib')
    site_packages_dir = os.path.join(pg_lib_dir, 'pg_steadytext', 'site-packages')

    error_msg = f"""
=================================================================
Missing required Python packages: {', '.join(missing_packages)}

The pg_steadytext extension requires these packages to function.

To fix this, run ONE of the following commands:

1. Install via make (recommended):
   cd /path/to/pg_steadytext
   sudo make install

2. Install to PostgreSQL's site-packages:
   sudo pip3 install --target={site_packages_dir} steadytext pyzmq numpy

3. Install system-wide:
   sudo pip3 install steadytext pyzmq numpy

4. Install to user directory:
   pip3 install --user steadytext pyzmq numpy

After installation, restart PostgreSQL and try again.
=================================================================
"""
    plpy.error(error_msg)

# Try to import our modules and cache them in GD
try:
    # Clear any previous module cache
    for key in list(GD.keys()):
        if key.startswith('module_'):
            del GD[key]

    # Import and cache modules
    import daemon_connector
    import cache_manager
    import security
    import config

    # Store modules in GD for reuse
    GD['module_daemon_connector'] = daemon_connector
    GD['module_cache_manager'] = cache_manager
    GD['module_security'] = security
    GD['module_config'] = config
    GD['steadytext_initialized'] = True

    plpy.notice(f"pg_steadytext Python environment initialized successfully from {python_module_dir}")
except ImportError as e:
    GD['steadytext_initialized'] = False
    pg_lib_dir = GD.get('pg_lib_dir', '/usr/lib/postgresql/17/lib')
    site_packages_dir = os.path.join(pg_lib_dir, 'pg_steadytext', 'site-packages')

    error_msg = f"""
=================================================================
Failed to import pg_steadytext modules from {python_module_dir}

Error: {str(e)}

This usually means the extension files are installed but Python
module files are missing or there's an import error.

To fix this:

1. Ensure all Python module files are present in:
   {python_module_dir}

2. Check that required packages are installed:
   sudo pip3 install --target={site_packages_dir} steadytext pyzmq numpy

3. Or reinstall the extension:
   cd /path/to/pg_steadytext
   sudo make install

After fixing, restart PostgreSQL and try again.
=================================================================
"""
    plpy.error(error_msg)
except Exception as e:
    GD['steadytext_initialized'] = False
    plpy.error(f"Unexpected error during initialization: {e}")
$c$;

-- AIDEV-NOTE: Initialization is now done on-demand in each function
-- This ensures proper initialization even across session boundaries

-- AIDEV-SECTION: CORE_FUNCTIONS
-- Core function: Synchronous text generation
-- Returns NULL if generation fails (no fallback text)
CREATE OR REPLACE FUNCTION steadytext_generate(
    prompt TEXT,
    max_tokens INT DEFAULT NULL,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE LEAKPROOF
AS $c$
# AIDEV-NOTE: Main text generation function that integrates with SteadyText daemon
# Fixed in v1.4.1 to use SELECT-only cache reads for true immutability
import json
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    # Initialize on demand
    plpy.execute("SELECT _steadytext_init_python()")
    # Check again after initialization
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Get configuration
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

# Resolve max_tokens, using the provided value or fetching the default
resolved_max_tokens = max_tokens
if resolved_max_tokens is None:
    rv = plpy.execute(plan, ["default_max_tokens"])
    resolved_max_tokens = json.loads(rv[0]["value"]) if rv else 512

# Resolve seed, using the provided value or fetching the default
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate inputs
if not prompt or not prompt.strip():
    plpy.error("Prompt cannot be empty")

if resolved_max_tokens < 1 or resolved_max_tokens > 4096:
    plpy.error("max_tokens must be between 1 and 4096")

if resolved_seed < 0:
    plpy.error("seed must be non-negative")

# Check if we should use cache
if use_cache:
    # Generate cache key consistent with SteadyText format
    # AIDEV-NOTE: Updated to match SteadyText's simple cache key format from utils.py
    # For generation: just the prompt (no parameters in key)
    cache_key = prompt

    # Try to get from cache first - SELECT ONLY (no UPDATE for immutability)
    cache_plan = plpy.prepare("""
        SELECT response 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["response"]:
        plpy.notice(f"Cache hit for key: {cache_key[:8]}...")
        return cache_result[0]["response"]

# Cache miss - generate new content
# Get configuration for daemon connection
host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])  
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create daemon connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Check if daemon should auto-start
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    started = connector.start_daemon()
    if not started:
        plpy.warning("Failed to auto-start daemon, will try direct generation")

# Try to generate via daemon or direct fallback
try:
    if connector.is_daemon_running():
        result = connector.generate(
            prompt=prompt,
            max_tokens=resolved_max_tokens,
            seed=resolved_seed
        )
    else:
        # Direct generation fallback
        from steadytext import generate as steadytext_generate
        result = steadytext_generate(
            prompt=prompt, 
            max_new_tokens=resolved_max_tokens,
            seed=resolved_seed
        )
    
    # AIDEV-NOTE: Cache writes removed for IMMUTABLE compliance
    # To populate cache, use the VOLATILE wrapper functions or external processes
    
    return result
    
except Exception as e:
    plpy.error(f"Generation failed: {str(e)}")
$c$;

-- Core function: Synchronous embedding generation
-- Returns NULL if embedding generation fails (no fallback vector)
CREATE OR REPLACE FUNCTION steadytext_embed(
    text_input TEXT,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS vector(1024)
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE LEAKPROOF
AS $c$
# AIDEV-NOTE: Embedding function that returns deterministic embeddings
# Fixed in v1.4.1 to use SELECT-only cache reads for true immutability
import json
import numpy as np
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    # Initialize on demand
    plpy.execute("SELECT _steadytext_init_python()")
    # Check again after initialization
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Resolve seed, using the provided value or fetching the default
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate input
if not text_input or not text_input.strip():
    plpy.warning("Empty text input provided, returning NULL")
    return None

if resolved_seed < 0:
    plpy.error("seed must be non-negative")

# Check cache first if enabled
if use_cache:
    # Generate cache key for embedding
    # AIDEV-NOTE: Use SHA256 for embeddings to match SteadyText's format
    # Embeddings use SHA256 hash of "embed:{text}"
    cache_key_input = f"embed:{text_input}"
    cache_key = hashlib.sha256(cache_key_input.encode()).hexdigest()

    # SELECT ONLY - no UPDATE for immutability
    cache_plan = plpy.prepare("""
        SELECT embedding 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["embedding"] is not None:
        plpy.notice(f"Cache hit for embedding key: {cache_key[:8]}...")
        return cache_result[0]["embedding"]

# Cache miss - generate new embedding
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Auto-start daemon if configured
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    connector.start_daemon()

# Generate embedding
try:
    if connector.is_daemon_running():
        result = connector.embed(text=text_input)
    else:
        # Direct embedding fallback
        from steadytext import embed as steadytext_embed
        result = steadytext_embed(text_input)
    
    # Convert to vector format if needed
    if result is not None:
        # Ensure it's a list/array
        if hasattr(result, 'tolist'):
            embedding_list = result.tolist()
        else:
            embedding_list = list(result)
        
        # AIDEV-NOTE: Cache writes removed for IMMUTABLE compliance
        
        return embedding_list
    else:
        plpy.error("Failed to generate embedding")
        
except Exception as e:
    plpy.error(f"Embedding generation failed: {str(e)}")
$c$;

-- AIDEV-SECTION: DAEMON_MANAGEMENT_FUNCTIONS
-- Daemon management functions
CREATE OR REPLACE FUNCTION steadytext_daemon_start()
RETURNS BOOLEAN
LANGUAGE plpython3u
AS $c$
# AIDEV-NOTE: Start the SteadyText daemon if not already running
import subprocess
import time
import json

try:
    # Get daemon configuration
    plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])
    host_rv = plpy.execute(plan, ["daemon_host"])
    port_rv = plpy.execute(plan, ["daemon_port"])

    host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"
    port = json.loads(port_rv[0]["value"]) if port_rv else 5555

    # Check if daemon is already running by trying to start it
    # SteadyText daemon start command is idempotent
    try:
        result = subprocess.run(['st', 'daemon', 'start'], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # Update health status
            health_plan = plpy.prepare("""
                UPDATE steadytext_daemon_health
                SET status = 'healthy',
                    last_heartbeat = NOW()
                WHERE daemon_id = 'default'
            """)
            plpy.execute(health_plan)
            return True
        else:
            plpy.warning(f"Failed to start daemon: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        plpy.warning("Timeout starting daemon")
        return False

except Exception as e:
    plpy.error(f"Error in daemon start: {e}")
    return False
$c$;

-- Get daemon status
CREATE OR REPLACE FUNCTION steadytext_daemon_status()
RETURNS TABLE(
    daemon_id TEXT,
    status TEXT,
    endpoint TEXT,
    last_heartbeat TIMESTAMPTZ,
    uptime_seconds INT
)
LANGUAGE plpython3u
AS $c$
# AIDEV-NOTE: Check SteadyText daemon health status
import json

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    # Initialize on demand
    plpy.execute("SELECT _steadytext_init_python()")
    # Check again after initialization
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

try:
    # Get cached modules from GD
    daemon_connector = GD.get('module_daemon_connector')
    if not daemon_connector:
        plpy.error("daemon_connector module not loaded")

    # Get configuration
    plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])
    host_rv = plpy.execute(plan, ["daemon_host"])
    port_rv = plpy.execute(plan, ["daemon_port"])

    host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"
    port = json.loads(port_rv[0]["value"]) if port_rv else 5555

    # Try to connect using cached module
    try:
        connector = daemon_connector.SteadyTextConnector(host, port)
        # Use check_health method if available
        if hasattr(connector, 'check_health'):
            health_info = connector.check_health()
            status = health_info.get('status', 'healthy')
        else:
            # If we can create connector, daemon is healthy
            status = 'healthy'
    except:
        status = 'unhealthy'

    # Update and return health status
    update_plan = plpy.prepare("""
        UPDATE steadytext_daemon_health
        SET status = $1,
            last_heartbeat = CASE WHEN $1 = 'healthy' THEN NOW() ELSE last_heartbeat END
        WHERE daemon_id = 'default'
        RETURNING daemon_id, status, endpoint, last_heartbeat,
                  EXTRACT(EPOCH FROM (NOW() - last_heartbeat))::INT as uptime_seconds
    """, ["text"])

    result = plpy.execute(update_plan, [status])
    return result

except Exception as e:
    plpy.warning(f"Error checking daemon status: {e}")
    # Return current status from table
    select_plan = plpy.prepare("""
        SELECT daemon_id, status, endpoint, last_heartbeat,
               EXTRACT(EPOCH FROM (NOW() - last_heartbeat))::INT as uptime_seconds
        FROM steadytext_daemon_health
        WHERE daemon_id = 'default'
    """)
    return plpy.execute(select_plan)
$c$;

-- Stop daemon
CREATE OR REPLACE FUNCTION steadytext_daemon_stop()
RETURNS BOOLEAN
LANGUAGE plpython3u
AS $c$
# AIDEV-NOTE: Stop the SteadyText daemon gracefully
import subprocess
import json

try:
    # Stop daemon using CLI
    result = subprocess.run(['st', 'daemon', 'stop'], capture_output=True, text=True)

    if result.returncode == 0:
        # Update health status
        health_plan = plpy.prepare("""
            UPDATE steadytext_daemon_health
            SET status = 'stopping',
                last_heartbeat = NOW()
            WHERE daemon_id = 'default'
        """)
        plpy.execute(health_plan)

        return True
    else:
        plpy.warning(f"Failed to stop daemon: {result.stderr}")
        return False

except Exception as e:
    plpy.error(f"Error stopping daemon: {e}")
    return False
$c$;

-- AIDEV-SECTION: CACHE_MANAGEMENT_FUNCTIONS
-- Cache management functions
CREATE OR REPLACE FUNCTION steadytext_cache_stats()
RETURNS TABLE(
    total_entries BIGINT,
    total_size_mb FLOAT,
    cache_hit_rate FLOAT,
    avg_access_count FLOAT,
    oldest_entry TIMESTAMPTZ,
    newest_entry TIMESTAMPTZ
)
LANGUAGE sql
STABLE PARALLEL SAFE
AS $c$
    SELECT
        COUNT(*)::BIGINT as total_entries,
        COALESCE(SUM(pg_column_size(response) + pg_column_size(embedding)) / 1024.0 / 1024.0, 0)::FLOAT as total_size_mb,
        COALESCE(SUM(CASE WHEN access_count > 1 THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0), 0)::FLOAT as cache_hit_rate,
        COALESCE(AVG(access_count), 0)::FLOAT as avg_access_count,
        MIN(created_at) as oldest_entry,
        MAX(created_at) as newest_entry
    FROM steadytext_cache;
$c$;

-- Clear cache
CREATE OR REPLACE FUNCTION steadytext_cache_clear()
RETURNS BIGINT
LANGUAGE sql
AS $c$
    WITH deleted AS (
        DELETE FROM steadytext_cache
        RETURNING *
    )
    SELECT COUNT(*) FROM deleted;
$c$;

-- AIDEV-SECTION: UPDATE_EVICTION_FUNCTIONS
-- Replace frecency-based eviction with age-based eviction
CREATE OR REPLACE FUNCTION steadytext_cache_evict_by_age(
    target_entries INT DEFAULT NULL,
    target_size_mb FLOAT DEFAULT NULL,
    batch_size INT DEFAULT 100,
    min_age_hours INT DEFAULT 1
)
RETURNS TABLE(
    evicted_count INT,
    freed_size_mb FLOAT,
    remaining_entries BIGINT,
    remaining_size_mb FLOAT
)
LANGUAGE plpgsql
AS $c$
DECLARE
    v_evicted_count INT := 0;
    v_freed_size_mb FLOAT := 0;
    v_current_entries BIGINT;
    v_current_size_mb FLOAT;
    v_batch_evicted INT;
    v_batch_freed_mb FLOAT;
BEGIN
    -- AIDEV-NOTE: Simplified eviction using age-based strategy (FIFO)
    -- This replaces the frecency-based eviction to maintain IMMUTABLE functions
    
    -- Get current cache statistics
    SELECT 
        COUNT(*),
        COALESCE(SUM(pg_column_size(response) + pg_column_size(embedding)) / 1024.0 / 1024.0, 0)
    INTO v_current_entries, v_current_size_mb
    FROM steadytext_cache;
    
    -- Set default targets if not provided
    IF target_entries IS NULL THEN
        SELECT value::INT INTO target_entries 
        FROM steadytext_config 
        WHERE key = 'cache_max_entries';
        target_entries := COALESCE(target_entries, 10000);
    END IF;
    
    IF target_size_mb IS NULL THEN
        SELECT value::FLOAT INTO target_size_mb 
        FROM steadytext_config 
        WHERE key = 'cache_max_size_mb';
        target_size_mb := COALESCE(target_size_mb, 1000);
    END IF;
    
    -- Evict in batches until we meet our targets
    WHILE (v_current_entries > target_entries OR v_current_size_mb > target_size_mb) LOOP
        -- Delete oldest entries (FIFO eviction)
        WITH deleted AS (
            DELETE FROM steadytext_cache
            WHERE id IN (
                SELECT id 
                FROM steadytext_cache
                WHERE created_at < NOW() - INTERVAL '1 hour' * min_age_hours
                ORDER BY created_at ASC  -- Oldest first
                LIMIT batch_size
            )
            RETURNING pg_column_size(response) + pg_column_size(embedding) as size_bytes
        )
        SELECT 
            COUNT(*),
            COALESCE(SUM(size_bytes) / 1024.0 / 1024.0, 0)
        INTO v_batch_evicted, v_batch_freed_mb
        FROM deleted;
        
        -- Break if nothing was evicted (all entries are too young)
        IF v_batch_evicted = 0 THEN
            EXIT;
        END IF;
        
        -- Update totals
        v_evicted_count := v_evicted_count + v_batch_evicted;
        v_freed_size_mb := v_freed_size_mb + v_batch_freed_mb;
        v_current_entries := v_current_entries - v_batch_evicted;
        v_current_size_mb := v_current_size_mb - v_batch_freed_mb;
        
        -- Log eviction batch
        INSERT INTO steadytext_audit_log (action, details)
        VALUES (
            'cache_eviction',
            jsonb_build_object(
                'evicted_count', v_batch_evicted,
                'freed_size_mb', v_batch_freed_mb,
                'eviction_type', 'age_based'
            )
        );
    END LOOP;
    
    -- Return results
    RETURN QUERY
    SELECT 
        v_evicted_count,
        v_freed_size_mb,
        v_current_entries,
        v_current_size_mb;
END;
$c$;


-- Update the scheduled eviction function to use age-based eviction
CREATE OR REPLACE FUNCTION steadytext_cache_scheduled_eviction()
RETURNS void
LANGUAGE plpgsql
AS $c$
DECLARE
    v_enabled BOOLEAN;
    v_result RECORD;
BEGIN
    -- Check if eviction is enabled
    SELECT value::BOOLEAN INTO v_enabled 
    FROM steadytext_config 
    WHERE key = 'cache_eviction_enabled';
    
    IF NOT COALESCE(v_enabled, TRUE) THEN
        RETURN;
    END IF;
    
    -- Perform age-based eviction
    SELECT * INTO v_result
    FROM steadytext_cache_evict_by_age();
    
    -- Log results if anything was evicted
    IF v_result.evicted_count > 0 THEN
        RAISE NOTICE 'Cache eviction completed: % entries evicted, % MB freed',
            v_result.evicted_count, v_result.freed_size_mb;
    END IF;
END;
$c$;

-- Update cache preview to show age instead of frecency
CREATE OR REPLACE FUNCTION steadytext_cache_preview_eviction(
    preview_count INT DEFAULT 10
)
RETURNS TABLE(
    cache_key TEXT,
    prompt TEXT,
    access_count INT,
    last_accessed TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    age_days FLOAT,
    size_bytes BIGINT
)
LANGUAGE sql
STABLE PARALLEL SAFE
AS $c$
    SELECT 
        cache_key,
        LEFT(prompt, 50) || CASE WHEN LENGTH(prompt) > 50 THEN '...' ELSE '' END as prompt,
        access_count,
        last_accessed,
        created_at,
        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 as age_days,
        pg_column_size(response) + pg_column_size(embedding) as size_bytes
    FROM steadytext_cache
    WHERE created_at < NOW() - INTERVAL '1 hour'  -- Respect min age
    ORDER BY created_at ASC  -- Oldest first
    LIMIT preview_count;
$c$;

-- Update cache analysis to reflect age-based strategy
CREATE OR REPLACE FUNCTION steadytext_cache_analyze_usage()
RETURNS TABLE(
    age_bucket TEXT,
    entry_count BIGINT,
    avg_access_count FLOAT,
    total_size_mb FLOAT,
    percentage_of_cache FLOAT
)
LANGUAGE sql
STABLE PARALLEL SAFE
AS $c$
    WITH cache_buckets AS (
        SELECT 
            CASE 
                WHEN created_at > NOW() - INTERVAL '1 hour' THEN '< 1 hour'
                WHEN created_at > NOW() - INTERVAL '1 day' THEN '1 hour - 1 day'
                WHEN created_at > NOW() - INTERVAL '7 days' THEN '1 day - 7 days'
                WHEN created_at > NOW() - INTERVAL '30 days' THEN '7 days - 30 days'
                ELSE '> 30 days'
            END as age_bucket,
            COUNT(*) as entry_count,
            AVG(access_count) as avg_access_count,
            SUM(pg_column_size(response) + pg_column_size(embedding)) / 1024.0 / 1024.0 as total_size_mb
        FROM steadytext_cache
        GROUP BY 1
    ),
    total AS (
        SELECT COUNT(*) as total_entries
        FROM steadytext_cache
    )
    SELECT 
        cb.age_bucket,
        cb.entry_count,
        cb.avg_access_count,
        cb.total_size_mb,
        (cb.entry_count::FLOAT / NULLIF(t.total_entries, 0) * 100)::FLOAT as percentage_of_cache
    FROM cache_buckets cb
    CROSS JOIN total t
    ORDER BY 
        CASE cb.age_bucket
            WHEN '< 1 hour' THEN 1
            WHEN '1 hour - 1 day' THEN 2
            WHEN '1 day - 7 days' THEN 3
            WHEN '7 days - 30 days' THEN 4
            ELSE 5
        END;
$c$;

-- AIDEV-NOTE: The view steadytext_cache_with_frecency is kept for compatibility
-- but now shows age_score instead of frecency_score
CREATE OR REPLACE VIEW steadytext_cache_with_frecency AS
SELECT *,
    -- Simple age-based score for compatibility (higher = older = more likely to evict)
    EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 AS frecency_score
FROM steadytext_cache;

COMMENT ON VIEW steadytext_cache_with_frecency IS 
'Compatibility view - frecency_score now represents age in days (v1.4.1+)';

-- Add comment explaining the cache strategy change
COMMENT ON TABLE steadytext_cache IS 
'Write-once cache for SteadyText results. Uses age-based eviction (FIFO) as of v1.4.1 to maintain IMMUTABLE function guarantees.';

-- Get extension version
CREATE OR REPLACE FUNCTION steadytext_version()
RETURNS TEXT
LANGUAGE sql
IMMUTABLE PARALLEL SAFE LEAKPROOF
AS $c$
    SELECT '1.4.2'::TEXT;
$c$;

CREATE OR REPLACE FUNCTION steadytext_config_get(key TEXT)
RETURNS TEXT
LANGUAGE sql
STABLE PARALLEL SAFE LEAKPROOF
AS $c$
    SELECT value::text FROM steadytext_config WHERE key = $1;
$c$;

-- AIDEV-SECTION: STRUCTURED_GENERATION_FUNCTIONS
-- Structured generation functions using llama.cpp grammars

-- Generate JSON with schema validation
CREATE OR REPLACE FUNCTION steadytext_generate_json(
    prompt TEXT,
    schema JSONB,
    max_tokens INT DEFAULT NULL,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
# AIDEV-NOTE: Generate JSON that conforms to a schema using llama.cpp grammars
# Fixed in v1.4.1 to use SELECT-only cache reads for true immutability
import json
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    plpy.execute("SELECT _steadytext_init_python()")
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Get configuration
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

# Resolve max_tokens
resolved_max_tokens = max_tokens
if resolved_max_tokens is None:
    rv = plpy.execute(plan, ["default_max_tokens"])
    resolved_max_tokens = json.loads(rv[0]["value"]) if rv else 512

# Resolve seed
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate inputs
if not prompt or not prompt.strip():
    plpy.error("Prompt cannot be empty")

if not schema:
    plpy.error("Schema cannot be empty")

# Convert JSONB to dict if needed
schema_dict = schema
if isinstance(schema, str):
    try:
        schema_dict = json.loads(schema)
    except json.JSONDecodeError as e:
        plpy.error(f"Invalid JSON schema: {e}")

# Check if we should use cache
if use_cache:
    # Generate cache key including schema
    # AIDEV-NOTE: Include schema in cache key for structured generation
    cache_key_input = f"{prompt}|json|{json.dumps(schema_dict, sort_keys=True)}"
    cache_key = hashlib.sha256(cache_key_input.encode()).hexdigest()

    # SELECT ONLY - no UPDATE for immutability
    cache_plan = plpy.prepare("""
        SELECT response 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["response"]:
        plpy.notice(f"Cache hit for JSON key: {cache_key[:8]}...")
        return cache_result[0]["response"]

# Cache miss - generate new content
host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Auto-start daemon if configured
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    connector.start_daemon()

# Generate structured output
try:
    if connector.is_daemon_running():
        result = connector.generate_json(
            prompt=prompt,
            schema=schema_dict,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    else:
        # Direct generation fallback
        from steadytext import generate_json as steadytext_generate_json
        result = steadytext_generate_json(
            prompt=prompt,
            schema=schema_dict,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    
    # AIDEV-NOTE: Cache writes removed for IMMUTABLE compliance
    
    return result
    
except Exception as e:
    plpy.error(f"JSON generation failed: {str(e)}")
$c$;

-- Generate text matching a regex pattern
CREATE OR REPLACE FUNCTION steadytext_generate_regex(
    prompt TEXT,
    pattern TEXT,
    max_tokens INT DEFAULT NULL,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
# AIDEV-NOTE: Generate text matching a regex pattern using llama.cpp grammars
# Fixed in v1.4.1 to use SELECT-only cache reads for true immutability
import json
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    plpy.execute("SELECT _steadytext_init_python()")
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Get configuration
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

# Resolve max_tokens
resolved_max_tokens = max_tokens
if resolved_max_tokens is None:
    rv = plpy.execute(plan, ["default_max_tokens"])
    resolved_max_tokens = json.loads(rv[0]["value"]) if rv else 512

# Resolve seed
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate inputs
if not prompt or not prompt.strip():
    plpy.error("Prompt cannot be empty")

if not pattern or not pattern.strip():
    plpy.error("Pattern cannot be empty")

# Check if we should use cache
if use_cache:
    # Generate cache key including pattern
    cache_key_input = f"{prompt}|regex|{pattern}"
    cache_key = hashlib.sha256(cache_key_input.encode()).hexdigest()

    # SELECT ONLY - no UPDATE for immutability
    cache_plan = plpy.prepare("""
        SELECT response 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["response"]:
        plpy.notice(f"Cache hit for regex key: {cache_key[:8]}...")
        return cache_result[0]["response"]

# Cache miss - generate new content
host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Auto-start daemon if configured
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    connector.start_daemon()

# Generate structured output
try:
    if connector.is_daemon_running():
        result = connector.generate_regex(
            prompt=prompt,
            pattern=pattern,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    else:
        # Direct generation fallback
        from steadytext import generate_regex as steadytext_generate_regex
        result = steadytext_generate_regex(
            prompt=prompt,
            regex=pattern,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    
    # AIDEV-NOTE: Cache writes removed for IMMUTABLE compliance
    
    return result
    
except Exception as e:
    plpy.error(f"Regex generation failed: {str(e)}")
$c$;

-- Generate text from a list of choices
CREATE OR REPLACE FUNCTION steadytext_generate_choice(
    prompt TEXT,
    choices TEXT[],
    max_tokens INT DEFAULT NULL,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
# AIDEV-NOTE: Generate text constrained to one of the provided choices
# Fixed in v1.4.1 to use SELECT-only cache reads for true immutability
import json
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    plpy.execute("SELECT _steadytext_init_python()")
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Get configuration
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

# Resolve max_tokens
resolved_max_tokens = max_tokens
if resolved_max_tokens is None:
    rv = plpy.execute(plan, ["default_max_tokens"])
    resolved_max_tokens = json.loads(rv[0]["value"]) if rv else 512

# Resolve seed
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate inputs
if not prompt or not prompt.strip():
    plpy.error("Prompt cannot be empty")

if not choices or len(choices) == 0:
    plpy.error("Choices list cannot be empty")

# Convert PostgreSQL array to Python list
choices_list = list(choices)

# Check if we should use cache
if use_cache:
    # Generate cache key including choices
    cache_key_input = f"{prompt}|choice|{json.dumps(sorted(choices_list))}"
    cache_key = hashlib.sha256(cache_key_input.encode()).hexdigest()

    # SELECT ONLY - no UPDATE for immutability
    cache_plan = plpy.prepare("""
        SELECT response 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["response"]:
        plpy.notice(f"Cache hit for choice key: {cache_key[:8]}...")
        return cache_result[0]["response"]

# Cache miss - generate new content
host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Auto-start daemon if configured
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    connector.start_daemon()

# Generate structured output
try:
    if connector.is_daemon_running():
        result = connector.generate_choice(
            prompt=prompt,
            choices=choices_list,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    else:
        # Direct generation fallback
        from steadytext import generate_choice as steadytext_generate_choice
        result = steadytext_generate_choice(
            prompt=prompt,
            choices=choices_list,
            max_tokens=resolved_max_tokens,
            seed=seed
        )
    
    # AIDEV-NOTE: Cache writes removed for IMMUTABLE compliance
    
    return result
    
except Exception as e:
    plpy.error(f"Choice generation failed: {str(e)}")
$c$;

-- AIDEV-SECTION: AI_SUMMARIZATION_AGGREGATES
-- AI summarization aggregate functions with TimescaleDB support

-- Helper function to extract facts from text using JSON generation
CREATE OR REPLACE FUNCTION ai_extract_facts(
    input_text text,
    max_facts integer DEFAULT 5
) RETURNS jsonb
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
    import json
    from plpy import quote_literal

    # Validate inputs
    if not input_text or not input_text.strip():
        return json.dumps({"facts": []})

    if max_facts <= 0 or max_facts > 50:
        plpy.error("max_facts must be between 1 and 50")

    # AIDEV-NOTE: Use steadytext's JSON generation with schema for structured fact extraction
    schema = {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": max_facts,
                "description": "Key facts extracted from the text"
            }
        },
        "required": ["facts"]
    }

    prompt = f"Extract up to {max_facts} key facts from this text: {input_text}"

    # Use daemon_connector for JSON generation
    plan = plpy.prepare(
        "SELECT steadytext_generate_json($1, $2::jsonb) as result",
        ["text", "jsonb"]
    )
    result = plpy.execute(plan, [prompt, json.dumps(schema)])

    if result and result[0]["result"]:
        try:
            return json.loads(result[0]["result"])
        except json.JSONDecodeError as e:
            plpy.warning(f"Failed to parse JSON response: {e}")
            return json.dumps({"facts": []})
        except Exception as e:
            plpy.warning(f"Unexpected error parsing response: {e}")
            return json.dumps({"facts": []})
    return json.dumps({"facts": []})
$c$;

-- Helper function to deduplicate facts using embeddings
CREATE OR REPLACE FUNCTION ai_deduplicate_facts(
    facts_array jsonb,
    similarity_threshold float DEFAULT 0.85
) RETURNS jsonb
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
    import json
    import numpy as np

    # Validate similarity threshold
    if similarity_threshold < 0.0 or similarity_threshold > 1.0:
        plpy.error("similarity_threshold must be between 0.0 and 1.0")

    try:
        facts = json.loads(facts_array)
    except (json.JSONDecodeError, TypeError) as e:
        plpy.warning(f"Invalid JSON input: {e}")
        return json.dumps([])

    if not facts or len(facts) == 0:
        return json.dumps([])

    # Extract text from fact objects if they have structure
    fact_texts = []
    for fact in facts:
        if isinstance(fact, dict) and "text" in fact:
            fact_texts.append(fact["text"])
        elif isinstance(fact, str):
            fact_texts.append(fact)

    if len(fact_texts) <= 1:
        return facts_array

    # Generate embeddings for all facts
    # AIDEV-NOTE: Consider batching embedding generation for better performance
    embeddings = []
    for text in fact_texts:
        plan = plpy.prepare("SELECT steadytext_embed($1) as embedding", ["text"])
        result = plpy.execute(plan, [text])
        if result and result[0]["embedding"]:
            embeddings.append(np.array(result[0]["embedding"]))

    # Deduplicate based on cosine similarity
    unique_indices = [0]  # Always keep first fact
    for i in range(1, len(embeddings)):
        is_duplicate = False
        for j in unique_indices:
            # Calculate cosine similarity with zero-norm protection
            norm_i = np.linalg.norm(embeddings[i])
            norm_j = np.linalg.norm(embeddings[j])

            if norm_i == 0 or norm_j == 0:
                # Treat zero-norm vectors as non-duplicate
                similarity = 0.0
            else:
                similarity = np.dot(embeddings[i], embeddings[j]) / (norm_i * norm_j)

            if similarity > similarity_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_indices.append(i)

    # Return deduplicated facts
    unique_facts = [facts[i] for i in unique_indices]
    return json.dumps(unique_facts)
$c$;

-- State accumulator function for AI summarization
CREATE OR REPLACE FUNCTION ai_summarize_accumulate(
    state jsonb,
    value text,
    metadata jsonb DEFAULT '{}'::jsonb
) RETURNS jsonb
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
    import json

    # Initialize state if null
    if state is None:
        state = {
            "facts": [],
            "samples": [],
            "stats": {
                "row_count": 0,
                "total_chars": 0,
                "min_length": None,
                "max_length": 0
            },
            "metadata": {}
        }
    else:
        try:
            state = json.loads(state)
        except (json.JSONDecodeError, TypeError) as e:
            plpy.error(f"Invalid state JSON: {e}")

    if value is None:
        return json.dumps(state)

    # Extract facts from the value
    plan = plpy.prepare("SELECT ai_extract_facts($1, 3) as facts", ["text"])
    result = plpy.execute(plan, [value])

    if result and result[0]["facts"]:
        try:
            extracted = json.loads(result[0]["facts"])
            if "facts" in extracted:
                state["facts"].extend(extracted["facts"])
        except (json.JSONDecodeError, TypeError):
            # Skip if fact extraction failed
            pass

    # Update statistics
    value_len = len(value)
    state["stats"]["row_count"] += 1
    state["stats"]["total_chars"] += value_len

    if state["stats"]["min_length"] is None or value_len < state["stats"]["min_length"]:
        state["stats"]["min_length"] = value_len
    if value_len > state["stats"]["max_length"]:
        state["stats"]["max_length"] = value_len

    # Sample every 10th row (up to 10 samples)
    if state["stats"]["row_count"] % 10 == 1 and len(state["samples"]) < 10:
        state["samples"].append(value[:200])  # First 200 chars

    # Merge metadata
    if metadata:
        try:
            meta = json.loads(metadata) if isinstance(metadata, str) else metadata
            for key, value in meta.items():
                if key not in state["metadata"]:
                    state["metadata"][key] = value
        except (json.JSONDecodeError, TypeError):
            # Skip invalid metadata
            pass

    return json.dumps(state)
$c$;

-- Combiner function for parallel aggregation
CREATE OR REPLACE FUNCTION ai_summarize_combine(
    state1 jsonb,
    state2 jsonb
) RETURNS jsonb
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
    import json

    if state1 is None:
        return state2
    if state2 is None:
        return state1

    try:
        s1 = json.loads(state1)
    except (json.JSONDecodeError, TypeError):
        return state2

    try:
        s2 = json.loads(state2)
    except (json.JSONDecodeError, TypeError):
        return state1

    # Combine facts
    combined_facts = s1.get("facts", []) + s2.get("facts", [])

    # Deduplicate facts if too many
    # AIDEV-NOTE: Threshold of 20 may need tuning based on usage patterns
    if len(combined_facts) > 20:
        plan = plpy.prepare(
            "SELECT ai_deduplicate_facts($1::jsonb) as deduped",
            ["jsonb"]
        )
        result = plpy.execute(plan, [json.dumps(combined_facts)])
        if result and result[0]["deduped"]:
            try:
                combined_facts = json.loads(result[0]["deduped"])
            except (json.JSONDecodeError, TypeError):
                # Keep original if deduplication failed
                pass

    # Combine samples (keep diverse set)
    combined_samples = s1.get("samples", []) + s2.get("samples", [])
    if len(combined_samples) > 10:
        # Simple diversity: take evenly spaced samples
        step = len(combined_samples) // 10
        combined_samples = combined_samples[::step][:10]

    # Combine statistics
    stats1 = s1.get("stats", {})
    stats2 = s2.get("stats", {})

    combined_stats = {
        "row_count": stats1.get("row_count", 0) + stats2.get("row_count", 0),
        "total_chars": stats1.get("total_chars", 0) + stats2.get("total_chars", 0),
        "min_length": min(
            stats1.get("min_length", float('inf')),
            stats2.get("min_length", float('inf'))
        ),
        "max_length": max(
            stats1.get("max_length", 0),
            stats2.get("max_length", 0)
        ),
        "combine_depth": max(
            stats1.get("combine_depth", 0),
            stats2.get("combine_depth", 0)
        ) + 1
    }

    # Merge metadata
    combined_metadata = {**s1.get("metadata", {}), **s2.get("metadata", {})}

    return json.dumps({
        "facts": combined_facts,
        "samples": combined_samples,
        "stats": combined_stats,
        "metadata": combined_metadata
    })
$c$;

-- Finalizer function to generate summary
CREATE OR REPLACE FUNCTION ai_summarize_finalize(
    state jsonb
) RETURNS text
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
    import json

    if state is None:
        return None

    try:
        state_data = json.loads(state)
    except (json.JSONDecodeError, TypeError):
        return "Unable to parse aggregation state"

    # Check if we have any data
    if state_data.get("stats", {}).get("row_count", 0) == 0:
        return "No data to summarize"

    # Build summary prompt based on combine depth
    combine_depth = state_data.get("stats", {}).get("combine_depth", 0)

    if combine_depth == 0:
        prompt_template = "Create a concise summary of this data: Facts: {facts}, Row count: {row_count}, Average length: {avg_length}"
    elif combine_depth < 3:
        prompt_template = "Synthesize these key facts into a coherent summary: {facts}, Total rows: {row_count}, Length range: {min_length}-{max_length} chars"
    else:
        prompt_template = "Identify major patterns from these aggregated facts: {facts}, Dataset size: {row_count} rows"

    # Calculate average length with division by zero protection
    stats = state_data.get("stats", {})
    row_count = stats.get("row_count", 0)
    if row_count > 0:
        avg_length = stats.get("total_chars", 0) // row_count
    else:
        avg_length = 0

    # Format facts for prompt
    facts = state_data.get("facts", [])[:10]  # Limit to top 10 facts
    facts_str = "; ".join(facts) if facts else "No specific facts extracted"

    # Build prompt
    prompt = prompt_template.format(
        facts=facts_str,
        row_count=row_count,
        avg_length=avg_length,
        min_length=stats.get("min_length", 0),
        max_length=stats.get("max_length", 0)
    )

    # Add metadata context if available
    metadata = state_data.get("metadata", {})
    if metadata:
        meta_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()])
        prompt += f". Context: {meta_str}"

    # Generate summary using steadytext
    plan = plpy.prepare("SELECT steadytext_generate($1) as summary", ["text"])
    result = plpy.execute(plan, [prompt])

    if result and result[0]["summary"]:
        return result[0]["summary"]
    return "Unable to generate summary"
$c$;

-- AIDEV-NOTE: Since we use STYPE = jsonb, PostgreSQL handles serialization automatically for parallel processing.

-- Create the main aggregate
CREATE OR REPLACE AGGREGATE ai_summarize(text, jsonb) (
    SFUNC = ai_summarize_accumulate,
    STYPE = jsonb,
    FINALFUNC = ai_summarize_finalize,
    COMBINEFUNC = ai_summarize_combine,
    PARALLEL = SAFE
);

-- Create partial aggregate for TimescaleDB continuous aggregates
CREATE OR REPLACE AGGREGATE ai_summarize_partial(text, jsonb) (
    SFUNC = ai_summarize_accumulate,
    STYPE = jsonb,
    COMBINEFUNC = ai_summarize_combine,
    PARALLEL = SAFE
);

-- Helper function to combine partial states for final aggregation
CREATE OR REPLACE FUNCTION ai_summarize_combine_states(
    state1 jsonb,
    partial_state jsonb
) RETURNS jsonb
LANGUAGE plpgsql
IMMUTABLE PARALLEL SAFE
AS $c$
BEGIN
    -- Simply use the combine function
    RETURN ai_summarize_combine(state1, partial_state);
END;
$c$;

-- Create final aggregate that works on partial results
CREATE OR REPLACE AGGREGATE ai_summarize_final(jsonb) (
    SFUNC = ai_summarize_combine_states,
    STYPE = jsonb,
    FINALFUNC = ai_summarize_finalize,
    PARALLEL = SAFE
);

-- Convenience function for single-value summarization
CREATE OR REPLACE FUNCTION ai_summarize_text(
    input_text text,
    metadata jsonb DEFAULT '{}'::jsonb
) RETURNS text
LANGUAGE sql
IMMUTABLE PARALLEL SAFE
AS $c$
    SELECT ai_summarize_finalize(
        ai_summarize_accumulate(NULL::jsonb, input_text, metadata)
    );
$c$;

-- Add helpful comments
COMMENT ON AGGREGATE ai_summarize(text, jsonb) IS
'AI-powered text summarization aggregate that handles non-transitivity through structured fact extraction';

COMMENT ON AGGREGATE ai_summarize_partial(text, jsonb) IS
'Partial aggregate for use with TimescaleDB continuous aggregates';

COMMENT ON AGGREGATE ai_summarize_final(jsonb) IS
'Final aggregate for completing partial aggregations from continuous aggregates';

COMMENT ON FUNCTION ai_extract_facts(text, integer) IS
'Extract structured facts from text using SteadyText JSON generation';

COMMENT ON FUNCTION ai_deduplicate_facts(jsonb, float) IS
'Deduplicate facts based on semantic similarity using embeddings';

-- AIDEV-SECTION: RERANKING_FUNCTIONS
-- Basic rerank function returning documents with scores
DROP FUNCTION IF EXISTS steadytext_rerank;
CREATE OR REPLACE FUNCTION steadytext_rerank(
    query text,
    documents text[],
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    return_scores boolean DEFAULT true,
    seed integer DEFAULT 42
) RETURNS TABLE(document text, score float)
AS $c$
    import json
    import logging
    from typing import List, Tuple
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    if not query:
        plpy.error("Query cannot be empty")
        
    if not documents or len(documents) == 0:
        return []
    
    # Check if initialized, if not, initialize now
    if not GD.get('steadytext_initialized', False):
        # Initialize on demand
        plpy.execute("SELECT _steadytext_init_python()")
        # Check again after initialization
        if not GD.get('steadytext_initialized', False):
            plpy.error("Failed to initialize pg_steadytext Python environment")
    
    # Get cached modules from GD
    daemon_connector = GD.get('module_daemon_connector')
    if not daemon_connector:
        plpy.error("daemon_connector module not loaded")
    
    try:
        connector = daemon_connector.SteadyTextConnector()
    except Exception as e:
        logger.error(f"Failed to initialize SteadyText connector: {e}")
        # Return empty result on error
        return []
    
    try:
        # Call rerank with scores always enabled for PostgreSQL
        results = connector.rerank(
            query=query,
            documents=list(documents),  # Convert from PostgreSQL array
            task=task,
            return_scores=True,  # Always get scores for PostgreSQL
            seed=seed
        )
        
        # Return results as tuples
        return results
        
    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        # Return empty result on error
        return []
$c$ LANGUAGE plpython3u IMMUTABLE PARALLEL SAFE;

-- Rerank function returning only documents (no scores)
CREATE OR REPLACE FUNCTION steadytext_rerank_docs_only(
    query text,
    documents text[],
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    seed integer DEFAULT 42
) RETURNS TABLE(document text)
AS $c$
    # Call the main rerank function and extract just documents
    results = plpy.execute(
        "SELECT document FROM steadytext_rerank($1, $2, $3, true, $4)",
        [query, documents, task, seed]
    )
    
    return [{"document": row["document"]} for row in results]
$c$ LANGUAGE plpython3u IMMUTABLE PARALLEL SAFE;

-- Rerank function with top-k filtering
CREATE OR REPLACE FUNCTION steadytext_rerank_top_k(
    query text,
    documents text[],
    top_k integer,
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    return_scores boolean DEFAULT true,
    seed integer DEFAULT 42
) RETURNS TABLE(document text, score float)
AS $c$
    # Validate top_k
    if top_k <= 0:
        plpy.error("top_k must be positive")
    
    # Call the main rerank function
    results = plpy.execute(
        "SELECT document, score FROM steadytext_rerank($1, $2, $3, true, $4) LIMIT $5",
        [query, documents, task, seed, top_k]
    )
    
    if return_scores:
        return results
    else:
        # Return without scores
        return [{"document": row["document"], "score": None} for row in results]
$c$ LANGUAGE plpython3u IMMUTABLE PARALLEL SAFE;

-- Async rerank function
CREATE OR REPLACE FUNCTION steadytext_rerank_async(
    query text,
    documents text[],
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    return_scores boolean DEFAULT true,
    seed integer DEFAULT 42
) RETURNS uuid
AS $c$
    import uuid
    import json
    import logging
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Prepare parameters
    params = {
        'query': query,
        'documents': documents,
        'task': task,
        'return_scores': return_scores,
        'seed': seed
    }
    
    # Insert into queue
    plpy.execute("""
        INSERT INTO steadytext_queue 
        (request_id, request_type, params, status, created_at, priority)
        VALUES ($1, 'rerank', $2::jsonb, 'pending', CURRENT_TIMESTAMP, 5)
    """, [request_id, json.dumps(params)])
    
    # Send notification to worker
    plpy.execute("NOTIFY steadytext_queue_notify")
    
    return request_id
$c$ LANGUAGE plpython3u VOLATILE;

-- Batch rerank function for multiple queries
CREATE OR REPLACE FUNCTION steadytext_rerank_batch(
    queries text[],
    documents text[],
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    return_scores boolean DEFAULT true,
    seed integer DEFAULT 42
) RETURNS TABLE(query_index integer, document text, score float)
AS $c$
    import json
    import logging
    from typing import List, Tuple
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    if not queries or len(queries) == 0:
        plpy.error("Queries cannot be empty")
        
    if not documents or len(documents) == 0:
        return []
    
    # Check if initialized, if not, initialize now
    if not GD.get('steadytext_initialized', False):
        # Initialize on demand
        plpy.execute("SELECT _steadytext_init_python()")
        # Check again after initialization
        if not GD.get('steadytext_initialized', False):
            plpy.error("Failed to initialize pg_steadytext Python environment")
    
    # Get cached modules from GD
    daemon_connector = GD.get('module_daemon_connector')
    if not daemon_connector:
        plpy.error("daemon_connector module not loaded")
    
    try:
        connector = daemon_connector.SteadyTextConnector()
    except Exception as e:
        logger.error(f"Failed to initialize SteadyText connector: {e}")
        return []
    
    all_results = []
    
    # Process each query
    for idx, query in enumerate(queries):
        try:
            # Call rerank for this query
            results = connector.rerank(
                query=query,
                documents=list(documents),
                task=task,
                return_scores=True,
                seed=seed
            )
            
            # Add query index to results
            for doc, score in results:
                all_results.append({
                    "query_index": idx,
                    "document": doc,
                    "score": score
                })
                
        except Exception as e:
            logger.error(f"Reranking failed for query {idx}: {e}")
            # Continue with next query
            continue
    
    return all_results
$c$ LANGUAGE plpython3u IMMUTABLE PARALLEL SAFE;

-- Batch async rerank function
CREATE OR REPLACE FUNCTION steadytext_rerank_batch_async(
    queries text[],
    documents text[],
    task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
    return_scores boolean DEFAULT true,
    seed integer DEFAULT 42
) RETURNS uuid[]
AS $c$
    import uuid
    import json
    
    request_ids = []
    
    # Create separate async request for each query
    for query in queries:
        request_id = str(uuid.uuid4())
        request_ids.append(request_id)
        
        params = {
            'query': query,
            'documents': documents,
            'task': task,
            'return_scores': return_scores,
            'seed': seed
        }
        
        plpy.execute("""
            INSERT INTO steadytext_queue 
            (request_id, request_type, params, status, created_at, priority)
            VALUES ($1, 'batch_rerank', $2::jsonb, 'pending', CURRENT_TIMESTAMP, 5)
        """, [request_id, json.dumps(params)])
    
    # Send notification to worker
    plpy.execute("NOTIFY steadytext_queue_notify")
    
    return request_ids
$c$ LANGUAGE plpython3u VOLATILE;

COMMENT ON FUNCTION steadytext_rerank IS 'Rerank documents by relevance to a query using AI model';
COMMENT ON FUNCTION steadytext_rerank_docs_only IS 'Rerank documents returning only sorted documents without scores';
COMMENT ON FUNCTION steadytext_rerank_top_k IS 'Rerank documents and return only top K results';
COMMENT ON FUNCTION steadytext_rerank_async IS 'Asynchronously rerank documents (returns request UUID)';
COMMENT ON FUNCTION steadytext_rerank_batch IS 'Rerank documents for multiple queries in batch';
COMMENT ON FUNCTION steadytext_rerank_batch_async IS 'Asynchronously rerank documents for multiple queries';

-- AIDEV-SECTION: VOLATILE_WRAPPER_FUNCTIONS
-- These functions provide cache-writing capability for users who need it
-- They wrap the IMMUTABLE functions and handle cache population

CREATE OR REPLACE FUNCTION steadytext_generate_cached(
    prompt TEXT,
    max_tokens INT DEFAULT NULL,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpgsql
VOLATILE
AS $c$
DECLARE
    v_result TEXT;
    v_cache_key TEXT;
    v_generation_params JSONB;
BEGIN
    -- AIDEV-NOTE: This VOLATILE wrapper allows cache writes
    -- Use this when you need automatic cache population
    
    -- Generate result using IMMUTABLE function
    v_result := steadytext_generate(prompt, max_tokens, true, seed);
    
    -- If result was generated (not from cache), store it
    IF v_result IS NOT NULL THEN
        -- Generate cache key
        v_cache_key := prompt;
        
        -- Check if already cached
        PERFORM 1 FROM steadytext_cache WHERE cache_key = v_cache_key;
        
        IF NOT FOUND THEN
            -- Resolve max_tokens default
            IF max_tokens IS NULL THEN
                SELECT value::INT INTO max_tokens 
                FROM steadytext_config 
                WHERE key = 'default_max_tokens';
                max_tokens := COALESCE(max_tokens, 512);
            END IF;
            
            v_generation_params := jsonb_build_object(
                'max_tokens', max_tokens,
                'seed', seed
            );
            
            -- Store in cache
            INSERT INTO steadytext_cache 
            (cache_key, prompt, response, model_name, seed, generation_params)
            VALUES (v_cache_key, prompt, v_result, 'steadytext-default', seed, v_generation_params)
            ON CONFLICT (cache_key) DO NOTHING;
        END IF;
    END IF;
    
    RETURN v_result;
END;
$c$;

CREATE OR REPLACE FUNCTION steadytext_embed_cached(
    text_input TEXT,
    seed INT DEFAULT 42
)
RETURNS vector(1024)
LANGUAGE plpgsql
VOLATILE
AS $c$
DECLARE
    v_result vector(1024);
    v_cache_key TEXT;
    v_cache_key_input TEXT;
BEGIN
    -- AIDEV-NOTE: This VOLATILE wrapper allows cache writes
    
    -- Generate result using IMMUTABLE function
    v_result := steadytext_embed(text_input, true, seed);
    
    -- If result was generated, store it
    IF v_result IS NOT NULL THEN
        -- Generate cache key
        v_cache_key_input := 'embed:' || text_input;
        v_cache_key := encode(digest(v_cache_key_input, 'sha256'), 'hex');
        
        -- Check if already cached
        PERFORM 1 FROM steadytext_cache WHERE cache_key = v_cache_key;
        
        IF NOT FOUND THEN
            -- Store in cache
            INSERT INTO steadytext_cache 
            (cache_key, prompt, embedding, model_name, seed)
            VALUES (v_cache_key, text_input, v_result, 'steadytext-embedding', seed)
            ON CONFLICT (cache_key) DO NOTHING;
        END IF;
    END IF;
    
    RETURN v_result;
END;
$c$;

-- Add comments explaining the wrapper functions
COMMENT ON FUNCTION steadytext_generate_cached IS 
'VOLATILE wrapper for steadytext_generate that handles cache population. Use when automatic caching is needed.';

COMMENT ON FUNCTION steadytext_embed_cached IS 
'VOLATILE wrapper for steadytext_embed that handles cache population. Use when automatic caching is needed.';

-- Add note about cache population strategies
COMMENT ON FUNCTION steadytext_generate IS 
'IMMUTABLE function for text generation. Only reads from cache, never writes. For automatic cache population, use steadytext_generate_cached.';

COMMENT ON FUNCTION steadytext_embed IS 
'IMMUTABLE function for embeddings. Only reads from cache, never writes. For automatic cache population, use steadytext_embed_cached.';

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO PUBLIC;

-- AIDEV-NOTE: This completes the base schema for pg_steadytext v1.4.2
--
-- AIDEV-SECTION: CHANGES_MADE_IN_REVIEW
-- The following issues were identified and fixed during review:
-- 1. Added missing columns: model_size, eos_string, response_size, daemon_endpoint
-- 2. Enhanced queue table with priority, user_id, session_id, batch support
-- 3. Added rate limiting and audit logging tables
-- 4. Fixed cache key generation to use SHA256 and match SteadyText format
-- 5. Fixed daemon integration to use proper SteadyText API methods
-- 6. Added proper indexes for performance
--
-- AIDEV-TODO: Future versions should add:
-- - Async processing functions (steadytext_generate_async, steadytext_get_result)
-- - Streaming generation function (steadytext_generate_stream)
-- - Batch operations (steadytext_embed_batch)
-- - FAISS index operations (steadytext_index_create, steadytext_index_search)
-- - Worker management functions
-- - Enhanced security and rate limiting functions
-- - Support for Pydantic models in structured generation (needs JSON serialization)
-- - Tests for structured generation functions

-- AIDEV-NOTE: Added in v1.0.1 (2025-07-07):
-- Marked all deterministic functions as IMMUTABLE, PARALLEL SAFE, and LEAKPROOF (where allowed):
-- - steadytext_generate(), steadytext_embed(), steadytext_generate_json(),
--   steadytext_generate_regex(), steadytext_generate_choice() are IMMUTABLE PARALLEL SAFE
-- - steadytext_version() is IMMUTABLE PARALLEL SAFE LEAKPROOF
-- - steadytext_cache_stats() and steadytext_config_get() are STABLE PARALLEL SAFE
-- - steadytext_config_get() is also LEAKPROOF since it's a simple SQL function
-- This enables use with TimescaleDB and in aggregates, and improves query optimization

-- AIDEV-NOTE: Added in v1.1.0 (2025-07-08):
-- AI summarization aggregate functions with the following features:
-- 1. Structured fact extraction to mitigate non-transitivity
-- 2. Semantic deduplication using embeddings
-- 3. Statistical tracking (row counts, character lengths)
-- 4. Sample preservation for context
-- 5. Combine depth tracking for adaptive prompts
-- 6. Full TimescaleDB continuous aggregate support
-- 7. Serialization for distributed aggregation

-- AIDEV-NOTE: Updated in v1.2.0 (2025-07-08):
-- Improved AI summarization aggregate functions with:
-- 1. Better error handling throughout all functions
-- 2. Input validation for all parameters
-- 3. Protection against division by zero in cosine similarity calculations
-- 4. Specific exception handling instead of bare except clauses
-- 5. Proper handling of invalid JSON inputs
-- 6. Zero-norm vector protection in similarity calculations
-- 7. Graceful fallback when parsing fails
-- 8. FIXED: Removed serialization functions to resolve "serialization functions may be
--    specified only when the aggregate transition data type is internal" error

-- AIDEV-NOTE: Added in v1.3.0 (2025-07-09):
-- Reranking functions for query-document relevance scoring:
-- 1. Basic rerank function with optional score return
-- 2. Document-only variant for simplified output
-- 3. Top-k filtering for returning best matches
-- 4. Async processing support via queue system
-- 5. Batch reranking for multiple queries
-- 6. Integration with SteadyText daemon for Qwen3-Reranker-4B model
-- pg_steadytext--1.4.2--1.4.3.sql
-- Migration from version 1.4.2 to 1.4.3

-- AIDEV-NOTE: This migration fixes the following issues:
-- 1. Parameter name fix: max_tokens → max_new_tokens for direct generation fallback
-- 2. Mark functions as LEAKPROOF where appropriate for security
-- 3. Fix function overload conflict by removing single-argument embed function
-- 4. Fix UnboundLocalError in ai_summarize_accumulate function
-- 5. Fix rerank function return type issue

-- Update the version function
CREATE OR REPLACE FUNCTION steadytext_version()
RETURNS TEXT
LANGUAGE sql
IMMUTABLE PARALLEL SAFE LEAKPROOF
AS $c$
    SELECT '1.4.3'::TEXT;
$c$;

-- Fix steadytext_generate function to use max_new_tokens in fallback
CREATE OR REPLACE FUNCTION steadytext_generate(
    prompt TEXT,
    max_tokens INT DEFAULT NULL,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS TEXT
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
# AIDEV-NOTE: Main text generation function that integrates with SteadyText daemon
import json
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    # Initialize on demand
    plpy.execute("SELECT _steadytext_init_python()")
    # Check again after initialization
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Get configuration
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

# Resolve max_tokens, using the provided value or fetching the default
resolved_max_tokens = max_tokens
if resolved_max_tokens is None:
    rv = plpy.execute(plan, ["default_max_tokens"])
    resolved_max_tokens = json.loads(rv[0]["value"]) if rv else 512

# Resolve seed, using the provided value or fetching the default
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate inputs
if not prompt or not prompt.strip():
    plpy.error("Prompt cannot be empty")

if resolved_max_tokens < 1 or resolved_max_tokens > 4096:
    plpy.error("max_tokens must be between 1 and 4096")

if resolved_seed < 0:
    plpy.error("seed must be non-negative")

# Check if we should use cache
if use_cache:
    # Generate cache key consistent with SteadyText format
    # For generation: just the prompt (no parameters in key)
    cache_key = prompt

    # Try to get from cache first
    cache_plan = plpy.prepare("""
        SELECT response 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["response"]:
        plpy.notice(f"Cache hit for key: {cache_key[:8]}...")
        return cache_result[0]["response"]

# Cache miss - generate new content
# Get configuration for daemon connection
host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])  
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create daemon connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Check if daemon should auto-start
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    started = connector.start_daemon()
    if not started:
        plpy.warning("Failed to auto-start daemon, will try direct generation")

# Try to generate via daemon or direct fallback
try:
    if connector.is_daemon_running():
        result = connector.generate(
            prompt=prompt,
            max_tokens=resolved_max_tokens,
            seed=resolved_seed
        )
    else:
        # Direct generation fallback
        from steadytext import generate as steadytext_generate
        result = steadytext_generate(
            prompt=prompt, 
            max_new_tokens=resolved_max_tokens,
            seed=resolved_seed
        )
    
    return result
    
except Exception as e:
    plpy.error(f"Generation failed: {str(e)}")
$c$;

CREATE OR REPLACE FUNCTION steadytext_embed(
    text_input TEXT,
    use_cache BOOLEAN DEFAULT TRUE,
    seed INT DEFAULT 42
)
RETURNS vector(1024)
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
# AIDEV-NOTE: Embedding function that returns deterministic embeddings
import json
import numpy as np
import hashlib

# Check if initialized, if not, initialize now
if not GD.get('steadytext_initialized', False):
    # Initialize on demand
    plpy.execute("SELECT _steadytext_init_python()")
    # Check again after initialization
    if not GD.get('steadytext_initialized', False):
        plpy.error("Failed to initialize pg_steadytext Python environment")

# Get cached modules from GD
daemon_connector = GD.get('module_daemon_connector')
if not daemon_connector:
    plpy.error("daemon_connector module not loaded")

# Resolve seed, using the provided value or fetching the default
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])
resolved_seed = seed
if resolved_seed is None:
    rv = plpy.execute(plan, ["default_seed"])
    resolved_seed = json.loads(rv[0]["value"]) if rv else 42

# Validate input
if not text_input or not text_input.strip():
    plpy.warning("Empty text input provided, returning NULL")
    return None

if resolved_seed < 0:
    plpy.error("seed must be non-negative")

# Check cache first if enabled
if use_cache:
    # Generate cache key for embedding
    # Embeddings use SHA256 hash of "embed:{text}"
    cache_key_input = f"embed:{text_input}"
    cache_key = hashlib.sha256(cache_key_input.encode()).hexdigest()

    # Try to get from cache
    cache_plan = plpy.prepare("""
        SELECT embedding 
        FROM steadytext_cache 
        WHERE cache_key = $1
    """, ["text"])
    
    cache_result = plpy.execute(cache_plan, [cache_key])
    if cache_result and cache_result[0]["embedding"] is not None:
        plpy.notice(f"Cache hit for embedding key: {cache_key[:8]}...")
        return cache_result[0]["embedding"]

# Cache miss - generate new embedding
plan = plpy.prepare("SELECT value FROM steadytext_config WHERE key = $1", ["text"])

host_rv = plpy.execute(plan, ["daemon_host"])
host = json.loads(host_rv[0]["value"]) if host_rv else "localhost"

port_rv = plpy.execute(plan, ["daemon_port"])
port = json.loads(port_rv[0]["value"]) if port_rv else 5555

# Create connector
connector = daemon_connector.SteadyTextConnector(host=host, port=port)

# Auto-start daemon if configured
auto_start_rv = plpy.execute(plan, ["daemon_auto_start"])
auto_start = json.loads(auto_start_rv[0]["value"]) if auto_start_rv else True

if auto_start and not connector.is_daemon_running():
    plpy.notice("Starting SteadyText daemon...")
    connector.start_daemon()

# Generate embedding
try:
    if connector.is_daemon_running():
        result = connector.embed(text=text_input)
    else:
        # Direct embedding fallback
        from steadytext import embed as steadytext_embed
        result = steadytext_embed(text_input)
    
    # Convert to vector format if needed
    if result is not None:
        # Ensure it's a list/array
        if hasattr(result, 'tolist'):
            embedding_list = result.tolist()
        else:
            embedding_list = list(result)
        
        return embedding_list
    else:
        plpy.error("Failed to generate embedding")
        
except Exception as e:
    plpy.error(f"Embedding generation failed: {str(e)}")
$c$;

-- Drop the single-argument embed overload if it exists (causes function overload conflicts)
DROP FUNCTION IF EXISTS steadytext_embed(TEXT);

-- Fix ai_summarize_accumulate UnboundLocalError
CREATE OR REPLACE FUNCTION ai_summarize_accumulate(
    state jsonb,
    value text,
    metadata jsonb DEFAULT '{}'::jsonb
) RETURNS jsonb
LANGUAGE plpython3u
IMMUTABLE PARALLEL SAFE
AS $c$
import json

old_state = state

if old_state is None:
    accum = {
        "facts": [],
        "samples": [],
        "stats": {
            "row_count": 0,
            "total_chars": 0,
            "min_length": None,
            "max_length": 0
        },
        "metadata": {}
    }
else:
    try:
        accum = json.loads(old_state)
    except (json.JSONDecodeError, TypeError) as e:
        plpy.error(f"Invalid state JSON: {e}")

if value is None:
    return json.dumps(accum)

# Extract facts from the value
plan = plpy.prepare("SELECT ai_extract_facts($1, 3) as facts", ["text"])
result = plpy.execute(plan, [value])

if result and result[0]["facts"]:
    try:
        extracted = json.loads(result[0]["facts"])
        if "facts" in extracted:
            accum["facts"].extend(extracted["facts"])
    except (json.JSONDecodeError, TypeError):
        pass

# Update statistics
value_len = len(value)
accum["stats"]["row_count"] += 1
accum["stats"]["total_chars"] += value_len
if accum["stats"]["min_length"] is None or value_len < accum["stats"]["min_length"]:
    accum["stats"]["min_length"] = value_len
if value_len > accum["stats"]["max_length"]:
    accum["stats"]["max_length"] = value_len

# Sample every 10th row (up to 10 samples)
if accum["stats"]["row_count"] % 10 == 1 and len(accum["samples"]) < 10:
    accum["samples"].append(value[:200])

# Merge metadata
if metadata:
    try:
        meta = json.loads(metadata) if isinstance(metadata, str) else metadata
        for k, v in meta.items():
            if k not in accum["metadata"]:
                accum["metadata"][k] = v
    except (json.JSONDecodeError, TypeError):
        pass

return json.dumps(accum)
$c$;

-- Fix rerank function return type issue
-- First rename the implementation function
DO $$
BEGIN
    -- Only run if steadytext_rerank_impl does NOT exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'steadytext_rerank_impl'
          AND pg_function_is_visible(oid)
    ) THEN
        EXECUTE $cmd$
            ALTER FUNCTION steadytext_rerank(text, text[], text, boolean, integer) RENAME TO steadytext_rerank_impl;
        $cmd$;

        EXECUTE $cmd$
            CREATE OR REPLACE FUNCTION steadytext_rerank(
                query text,
                documents text[],
                task text DEFAULT 'Given a web search query, retrieve relevant passages that answer the query',
                return_scores boolean DEFAULT true,
                seed integer DEFAULT 42
            ) RETURNS SETOF record
            LANGUAGE sql IMMUTABLE PARALLEL SAFE
            AS $c$
              SELECT document, score FROM steadytext_rerank_impl($1, $2, $3, $4, $5);
            $c$;
        $cmd$;
    END IF;
END
$$;

-- Update config function to be more secure
CREATE OR REPLACE FUNCTION steadytext_config_set(key TEXT, value TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $c$
BEGIN
    INSERT INTO steadytext_config (key, value)
    VALUES (key, to_jsonb(value))
    ON CONFLICT (key) DO UPDATE
    SET value = to_jsonb(EXCLUDED.value),
        updated_at = NOW(),
        updated_by = current_user;
END;
$c$;

-- AIDEV-NOTE: Migration completed successfully
-- Changes in v1.4.3:
-- 1. Fixed parameter name from max_tokens to max_new_tokens in direct generation fallback
-- 2. Added LEAKPROOF to appropriate functions for security
-- 3. Removed conflicting single-argument steadytext_embed overload
-- 4. Fixed UnboundLocalError in ai_summarize_accumulate by using old_state/accum pattern
-- 5. Fixed rerank function return type by creating proper SQL wrapper
