# API routes
from fastapi import APIRouter, HTTPException
from .schemas import ChatRequest, ChatResponse, MessageAction
from .llm_client import LLMClient
from ..behavior import BehaviorCoordinator
from ..behavior.models import BehaviorConfig

router = APIRouter()

# Initialize behavior coordinator (can be moved to dependency injection)
behavior_coordinator = None

def get_behavior_coordinator(request: ChatRequest) -> BehaviorCoordinator:
    """Get or create behavior coordinator with settings"""
    # Create config from request settings
    settings = request.behavior_settings
    if settings:
        config = BehaviorConfig(
            enable_segmentation=settings.enable_segmentation,
            enable_typo=settings.enable_typo,
            enable_recall=settings.enable_recall,
            enable_emotion_detection=settings.enable_emotion_detection,
            base_typo_rate=settings.base_typo_rate,
            typo_recall_rate=settings.typo_recall_rate,
        )
    else:
        config = BehaviorConfig()

    return BehaviorCoordinator(config=config)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with natural message behavior simulation
    """
    try:
        # Get LLM response
        client = LLMClient(request.llm_config)
        response_text = await client.chat(request.messages)
        await client.close()

        # Process message with behavior system
        coordinator = get_behavior_coordinator(request)
        message_segments = coordinator.process_message(response_text)

        # Convert segments to actions
        actions = []

        for i, segment in enumerate(message_segments):
            # Add pause before segment (if any)
            if segment.pause_before > 0:
                actions.append(MessageAction(
                    type="pause",
                    delay=segment.pause_before
                ))

            # Check if this is a typo that will be recalled
            is_recalled = False
            if i + 1 < len(message_segments):
                # Check if next segment is correction (same text but no typo)
                next_seg = message_segments[i + 1]
                if segment.has_typo and not next_seg.has_typo:
                    # This might be a typo-recall pair
                    # Simple heuristic: if texts are similar, it's a correction
                    is_recalled = True

            # Show typing indicator
            actions.append(MessageAction(
                type="typing_start",
                delay=0.0
            ))

            # Send message segment
            actions.append(MessageAction(
                type="send" if not is_recalled else "recall",
                text=segment.text,
                delay=0.1,  # Small delay after typing starts
                typing_speed=segment.typing_speed,
                metadata={
                    "has_typo": segment.has_typo,
                    "is_recalled": is_recalled
                }
            ))

            # Hide typing indicator
            actions.append(MessageAction(
                type="typing_end",
                delay=0.0
            ))

        # Get detected emotion for metadata
        emotion = coordinator.get_emotion(response_text)

        return ChatResponse(
            actions=actions,
            raw_response=response_text,
            metadata={
                "emotion": emotion.value,
                "segment_count": len(message_segments)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok"}