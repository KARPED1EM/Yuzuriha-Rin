#!/usr/bin/env python
"""Test database functionality"""

import asyncio
from datetime import datetime
from src.message_server.database import MessageDatabase
from src.message_server.models import Message, MessageType

async def test_database():
    print("Testing database functionality...")

    db = MessageDatabase("data/test_messages.db")

    test_message = Message(
        id="test-msg-1",
        conversation_id="test-conv-1",
        sender_id="user",
        type=MessageType.TEXT,
        content="Hello, this is a test message",
        timestamp=datetime.now().timestamp(),
        metadata={"test": True}
    )

    success = db.save_message(test_message)
    print(f"✓ Save message: {'Success' if success else 'Failed'}")

    messages = db.get_messages("test-conv-1")
    print(f"✓ Get messages: Found {len(messages)} message(s)")

    if messages:
        msg = messages[0]
        print(f"  - ID: {msg.id}")
        print(f"  - Content: {msg.content}")
        print(f"  - Sender: {msg.sender_id}")

    success = db.recall_message("test-msg-1", "test-conv-1")
    print(f"✓ Recall message: {'Success' if success else 'Failed'}")

    recalled_msg = db.get_message_by_id("test-msg-1")
    if recalled_msg:
        print(f"  - Type after recall: {recalled_msg.type}")

    success = db.clear_conversation("test-conv-1")
    print(f"✓ Clear conversation: {'Success' if success else 'Failed'}")

    messages_after_clear = db.get_messages("test-conv-1")
    print(f"✓ Messages after clear: {len(messages_after_clear)}")

    print("\nDatabase tests completed!")

if __name__ == "__main__":
    asyncio.run(test_database())
