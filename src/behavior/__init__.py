"""
Message Behavior System

This module handles natural message behaviors including:
- Message segmentation (with ML model interface for future integration)
- Typo injection based on emotion
- Recall/resend logic
- Pause duration prediction
"""

from .coordinator import BehaviorCoordinator
from .models import MessageSegment, BehaviorConfig, EmotionState

__all__ = [
    "BehaviorCoordinator",
    "MessageSegment",
    "BehaviorConfig",
    "EmotionState",
]
