"""
Quick start script for Yuzuriha Rin virtual character system
"""

import sys
import os
import io
import socket

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def find_free_port(start_port=8000, max_port=9000):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports available in range {start_port}-{max_port}")


if __name__ == "__main__":
    import uvicorn
    from src.api.main import app

    # Find an available port
    port = find_free_port()

    print("=" * 60)
    print("Yuzuriha Rin Virtual Character System")
    print("=" * 60)
    print("\nStarting server...")
    print(f"  ✓ URL: http://localhost:{port}")
    print(f"  ✓ API: http://localhost:{port}/api/health")
    print(f"  ✓ Port: {port}")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
