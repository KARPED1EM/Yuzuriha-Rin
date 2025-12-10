"""
Debug mode startup script
"""
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    import uvicorn
    from src.api.main import app

    # Check frontend directory
    frontend_dir = os.path.abspath("frontend")
    print(f"\nFrontend directory: {frontend_dir}")
    print(f"Exists: {os.path.exists(frontend_dir)}")

    if os.path.exists(frontend_dir):
        print(f"Files:")
        for f in os.listdir(frontend_dir):
            print(f"  - {f}")

    print("\n" + "=" * 60)
    print("Starting server in DEBUG mode...")
    print("  ✓ URL: http://localhost:8000")
    print("\n⚠️  IMPORTANT: Please access via http://localhost:8000")
    print("   (Do NOT use http://0.0.0.0:8000 - WebSocket won't work)")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=False
    )
