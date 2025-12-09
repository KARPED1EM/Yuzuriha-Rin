#!/usr/bin/env python
"""Test imports of all major components"""

print("Testing imports...")

try:
    from src.config import (
        app_config,
        character_config,
        llm_defaults,
        behavior_defaults,
        typing_state_defaults,
        ui_defaults,
        websocket_config,
        database_config
    )
    print("✓ Config imports successful")
except Exception as e:
    print(f"✗ Config import failed: {e}")

try:
    from src.message_server import MessageService, WebSocketManager, Message, MessageType, TypingState
    print("✓ Message server imports successful")
except Exception as e:
    print(f"✗ Message server import failed: {e}")

try:
    from src.message_server.database import MessageDatabase
    print("✓ Database imports successful")
except Exception as e:
    print(f"✗ Database import failed: {e}")

try:
    from src.behavior.coordinator import BehaviorCoordinator
    from src.behavior.timeline import TimelineBuilder
    from src.behavior.models import BehaviorConfig
    print("✓ Behavior system imports successful")
except Exception as e:
    print(f"✗ Behavior system import failed: {e}")

try:
    from src.rin_client import RinClient
    print("✓ Rin client imports successful")
except Exception as e:
    print(f"✗ Rin client import failed: {e}")

try:
    from src.api.main import app
    print("✓ API imports successful")
except Exception as e:
    print(f"✗ API import failed: {e}")

print("\nAll import tests completed!")
