"""
Quick start script for Yuzuriha Rin virtual character system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from src.api.main import app

    print("=" * 60)
    print("Yuzuriha Rin Virtual Character System")
    print("=" * 60)
    print("\nKey Features:")
    print("  - Multi-LLM support (OpenAI/Anthropic/Custom)")
    print("  - WeChat-style playback timeline (send/pause/recall)")
    print("  - LLM-driven JSON replies with structured emotion map")
    print("  - Rule-based segmentation plus emotion-driven typo/recall behavior")
    print("  - Server-side history injection for consistent persona adherence")
    print("\nStarting server...")
    print("URL: http://localhost:8000")
    print("API: http://localhost:8000/api/health")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
