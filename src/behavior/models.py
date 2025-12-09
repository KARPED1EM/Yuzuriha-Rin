"""
Data models for behavior system
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


class EmotionState(str, Enum):
    """Emotion states that affect message behavior"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CONFUSED = "confused"


class MessageSegment(BaseModel):
    """A segment of a message with associated behaviors"""
    text: str
    pause_before: float = Field(default=0.0, description="Pause in seconds before sending this segment")
    typing_speed: float = Field(default=0.05, description="Seconds per character for typing animation")
    has_typo: bool = False
    typo_position: Optional[int] = None
    typo_char: Optional[str] = None


class BehaviorConfig(BaseModel):
    """Configuration for behavior system"""
    # Segmentation
    enable_segmentation: bool = True
    max_segment_length: int = 50  # Characters per segment
    min_pause_duration: float = 0.3  # Minimum pause between segments
    max_pause_duration: float = 2.5  # Maximum pause between segments

    # Typo injection
    enable_typo: bool = True
    base_typo_rate: float = 0.08  # 8% base chance of typo per segment
    emotion_typo_multiplier: dict = Field(default_factory=lambda: {
        EmotionState.NEUTRAL: 1.0,
        EmotionState.HAPPY: 0.8,
        EmotionState.EXCITED: 1.5,
        EmotionState.SAD: 1.2,
        EmotionState.ANGRY: 1.8,
        EmotionState.ANXIOUS: 2.0,
        EmotionState.CONFUSED: 1.3,
    })

    # Recall behavior
    enable_recall: bool = True
    typo_recall_rate: float = 0.4  # 40% chance to recall and fix typo
    recall_delay: float = 1.5  # Seconds before recalling
    retype_delay: float = 0.8  # Seconds before sending corrected version

    # Emotion detection
    enable_emotion_detection: bool = True
