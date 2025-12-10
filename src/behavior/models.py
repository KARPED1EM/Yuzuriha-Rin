"""
Data models for behavior system
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional
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
    """
    A semantic unit produced by the segmenter before playback expansion.
    Each segment becomes one or more playback actions later.
    """
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlaybackAction(BaseModel):
    """A single step in the playback timeline."""
    type: Literal["send", "pause", "recall", "typing_start", "typing_end", "wait"]
    text: Optional[str] = None
    timestamp: float = Field(default=0.0, ge=0.0, description="Execution timestamp in seconds relative to start")
    duration: float = Field(default=0.0, ge=0.0, description="Duration in seconds for pause/wait actions")
    message_id: Optional[str] = Field(default=None, description="Identifier for the message created by this action")
    target_id: Optional[str] = Field(default=None, description="Identifier of the message affected by this action")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BehaviorConfig(BaseModel):
    """Configuration for behavior system"""
    # Segmentation
    enable_segmentation: bool = True
    max_segment_length: int = 50  # Characters per segment (used when ML model disabled)
    min_pause_duration: float = 0.4  # Minimum random interval between segments
    max_pause_duration: float = 2.5  # Maximum random interval between segments

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
    recall_delay: float = 1.2  # Seconds before recalling
    retype_delay: float = 0.6  # Seconds before sending corrected version

    # Emotion detection
    enable_emotion_detection: bool = True
