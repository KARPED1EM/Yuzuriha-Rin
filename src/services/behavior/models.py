from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional
from enum import Enum


class EmotionState(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CONFUSED = "confused"


class MessageSegment(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlaybackAction(BaseModel):
    type: Literal["send", "pause", "recall", "typing_start", "typing_end", "wait", "image"]
    text: Optional[str] = None
    timestamp: float = Field(default=0.0, ge=0.0)
    duration: float = Field(default=0.0, ge=0.0)
    message_id: Optional[str] = None
    target_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
