# Pydantic schemas for API
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class LLMConfig(BaseModel):
    provider: Literal["openai", "anthropic", "custom"] = "openai"
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    system_prompt: str = "You are a helpful assistant."

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class BehaviorSettings(BaseModel):
    """Settings for message behavior system"""
    enable_segmentation: bool = True
    enable_typo: bool = True
    enable_recall: bool = True
    enable_emotion_detection: bool = True
    base_typo_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    typo_recall_rate: float = Field(default=0.4, ge=0.0, le=1.0)

class ChatRequest(BaseModel):
    llm_config: LLMConfig
    messages: List[ChatMessage]
    character_name: str = "Rie"
    behavior_settings: Optional[BehaviorSettings] = None

class MessageAction(BaseModel):
    """
    A single message action (send, recall, typing, etc.)
    """
    type: Literal["typing_start", "typing_end", "send", "recall", "pause"]
    text: Optional[str] = None  # Text content for 'send' and 'recall' actions
    delay: float = Field(default=0.0, description="Delay in seconds before this action")
    typing_speed: Optional[float] = Field(default=None, description="Typing speed for animation (seconds per char)")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata (e.g., emotion, has_typo)")

class ChatResponse(BaseModel):
    actions: List[MessageAction]
    raw_response: str
    metadata: Optional[dict] = Field(default=None, description="Response metadata (e.g., detected emotion)")