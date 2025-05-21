import os

def ensure_directories(directories=None):
    """Ensure directories exist."""
    if not directories:
        return
    for d in directories:
        os.makedirs(d, exist_ok=True)