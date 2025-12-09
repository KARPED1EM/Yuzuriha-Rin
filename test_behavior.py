#!/usr/bin/env python
"""Test behavior system"""

from src.behavior.coordinator import BehaviorCoordinator
from src.behavior.models import BehaviorConfig

def test_behavior():
    print("Testing behavior system...")

    coordinator = BehaviorCoordinator(BehaviorConfig())

    test_text = "你好！我是Rin。今天天气真不错呢，我们一起出去玩吧！"

    timeline = coordinator.process_message(test_text, emotion_map={"happy": "high"})

    print(f"✓ Generated {len(timeline)} actions")

    action_types = {}
    for action in timeline:
        action_types[action.type] = action_types.get(action.type, 0) + 1

    print("\nAction breakdown:")
    for action_type, count in action_types.items():
        print(f"  - {action_type}: {count}")

    print("\nFirst 10 actions with timestamps:")
    for i, action in enumerate(timeline[:10]):
        print(f"  {i+1}. [{action.timestamp:.2f}s] {action.type}", end="")
        if action.text:
            print(f" - '{action.text[:30]}...'", end="")
        if action.duration:
            print(f" (duration: {action.duration:.2f}s)", end="")
        print()

    print("\nBehavior system test completed!")

if __name__ == "__main__":
    test_behavior()
