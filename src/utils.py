import os

def ensure_directories():
    """Ensure output and log directories exist."""
    os.makedirs('output', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
