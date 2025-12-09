# Implementation Guide

This document explains the implementation of the Rie Kugimiya virtual character system, focusing on the behavior simulation architecture.

## Architecture Overview

The system is divided into three main layers:

```
┌─────────────────┐
│   Frontend UI   │  - Web interface with typing animations
│   (HTML/CSS/JS) │  - Real-time message display
└────────┬────────┘  - Recall effects and emotion indicators
         │
┌────────▼────────┐
│   FastAPI API   │  - REST endpoints
│                 │  - Request/response handling
└────────┬────────┘  - Configuration management
         │
┌────────▼────────┐
│  LLM Client     │  - Multi-provider support (OpenAI/Anthropic/Custom)
│                 │  - Async HTTP communication
└────────┬────────┘
         │
┌────────▼────────┐
│ Behavior System │  - Message segmentation (rule-based + ML interface)
│                 │  - Emotion detection
│                 │  - Typo injection
│                 │  - Recall simulation
└─────────────────┘
```

## Behavior System Components

### 1. Message Segmentation (`src/behavior/segmenter.py`)

The segmentation module provides a flexible interface that supports both rule-based and ML-based implementations:

**BaseSegmenter (Abstract Class)**
- Defines the interface for all segmenters
- Method: `segment(text: str) -> List[str]`

**RuleBasedSegmenter**
- Current implementation using punctuation and length heuristics
- Splits text at natural boundaries (periods, commas, etc.)
- Configurable max segment length
- Serves as fallback when ML model is unavailable

**MLSegmenter (Placeholder)**
- Interface ready for BiLSTM-CRF model integration
- Will load trained model from checkpoint
- Falls back to rule-based if model unavailable

**SmartSegmenter (Recommended)**
- Automatically chooses between ML and rule-based
- Seamlessly switches when model becomes available
- Production-ready with fallback support

### 2. Emotion Detection (`src/behavior/emotion.py`)

**EmotionDetector**
- Keyword-based emotion detection
- Supports 7 emotion states: neutral, happy, excited, sad, angry, anxious, confused
- Chinese and English keyword support
- Emoji detection
- Returns both emotion type and intensity

**Supported Emotions:**
- `NEUTRAL`: Default state
- `HAPPY`: Joy, happiness
- `EXCITED`: High energy, enthusiasm
- `SAD`: Sadness, disappointment
- `ANGRY`: Frustration, anger
- `ANXIOUS`: Nervousness, worry
- `CONFUSED`: Uncertainty, confusion

### 3. Typo Injection (`src/behavior/typo.py`)

**TypoInjector**
- Simulates realistic typing errors
- Supports both Chinese and English
- Chinese: Similar character substitution
- English: Keyboard neighbor substitution
- Configurable typo rate (probability)
- Emotion-aware typo frequency

**Typo Strategy:**
- Position: Prefers middle-to-end of text (more realistic)
- Character selection: Only replaceable characters (has similar char or keyboard neighbor)
- Preserves case for English

### 4. Pause Prediction (`src/behavior/pause.py`)

**PausePredictor**
- Predicts natural pause durations between segments
- Emotion-aware pause timing
- Typing speed prediction based on emotion
- First/last segment handling

**Pause Factors:**
- Emotion state (excited = faster, sad = slower)
- Segment length (longer text = slightly longer pause)
- Position (last segment may have longer pause)

### 5. Behavior Coordinator (`src/behavior/coordinator.py`)

**BehaviorCoordinator**
- Main orchestrator for all behavior components
- Processes messages through the full pipeline
- Configurable via `BehaviorConfig`

**Processing Pipeline:**
1. Detect emotion from text
2. Segment message into chunks
3. For each segment:
   - Calculate pause duration
   - Calculate typing speed
   - Optionally inject typo
   - Decide on recall behavior
4. Return list of `MessageSegment` objects

## API Integration

### Request Schema (`src/api/schemas.py`)

**ChatRequest:**
```python
{
    "llm_config": {
        "provider": "openai",
        "api_key": "sk-...",
        "model": "gpt-3.5-turbo",
        "system_prompt": "..."
    },
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "character_name": "Rie",
    "behavior_settings": {  # Optional
        "enable_segmentation": true,
        "enable_typo": true,
        "enable_recall": true,
        "base_typo_rate": 0.08,
        "typo_recall_rate": 0.4
    }
}
```

**ChatResponse:**
```python
{
    "actions": [
        {"type": "typing_start", "delay": 0.0},
        {"type": "send", "text": "你好！", "delay": 0.1, "typing_speed": 0.05},
        {"type": "typing_end", "delay": 0.0},
        {"type": "pause", "delay": 0.8},
        {"type": "typing_start", "delay": 0.0},
        {"type": "send", "text": "今天天气不错呢", "delay": 0.1, "typing_speed": 0.05},
        {"type": "typing_end", "delay": 0.0}
    ],
    "raw_response": "你好！今天天气不错呢",
    "metadata": {
        "emotion": "happy",
        "segment_count": 2
    }
}
```

### Message Action Types

1. **typing_start**: Show typing indicator
2. **typing_end**: Hide typing indicator
3. **send**: Display message with typing animation
4. **recall**: Mark previous message as recalled (strikethrough)
5. **pause**: Wait before next action

## Frontend Implementation

### Typing Animation (`frontend/chat.js`)

The frontend plays actions sequentially:

1. Wait for `delay` before each action
2. Handle each action type:
   - `typing_start`: Show typing indicator (3 bouncing dots)
   - `send`: Animate text character-by-character
   - `recall`: Strike through previous message, then send correction
   - `pause`: Silent wait (creates natural rhythm)

### Visual Features

- **Typing animation**: Character-by-character reveal
- **Typing indicator**: Animated dots while processing
- **Recall effect**: Strikethrough + fade animation
- **Emotion indicators**: Colored border based on detected emotion
- **Smooth scrolling**: Auto-scroll to latest message

## ML Model Integration (Future)

To integrate the BiLSTM-CRF segmentation model:

1. Train the model (see `scripts/train_segmenter.py` - to be implemented)
2. Save model checkpoint to `data/models/segmenter.pth`
3. Update `MLSegmenter._load_model()`:
   ```python
   import torch
   self.model = torch.load(self.model_path)
   self.model.eval()
   ```
4. Implement `MLSegmenter.segment()` with inference logic
5. Pass `model_path` to `BehaviorCoordinator` initialization

The system will automatically use the ML model when available, with seamless fallback to rule-based segmentation.

## Configuration

### Behavior Settings

All behavior can be controlled via `BehaviorConfig`:

```python
config = BehaviorConfig(
    enable_segmentation=True,      # Enable message segmentation
    enable_typo=True,               # Enable typo injection
    enable_recall=True,             # Enable recall behavior
    enable_emotion_detection=True,  # Enable emotion detection

    max_segment_length=50,          # Max chars per segment
    min_pause_duration=0.3,         # Min pause (seconds)
    max_pause_duration=2.5,         # Max pause (seconds)

    base_typo_rate=0.08,           # 8% base typo chance
    typo_recall_rate=0.4,          # 40% chance to recall typo
    recall_delay=1.5,              # Delay before recall
    retype_delay=0.8,              # Delay before correction
)
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Tests cover:
- Segmentation (rule-based)
- Emotion detection
- Typo injection
- Recall probability
- End-to-end behavior coordination

## Development Workflow

1. **Start backend**:
   ```bash
   python -m src.api.main
   ```

2. **Access frontend**: `http://localhost:8000`

3. **Test behavior**:
   - Configure LLM settings
   - Send messages
   - Observe segmentation, pauses, typos, recalls

4. **Adjust behavior**:
   - Modify `BehaviorConfig` in `routes.py`
   - Or send custom settings in API requests

## Next Steps

- [ ] Implement BiLSTM-CRF model training
- [ ] Add more sophisticated emotion detection (sentiment analysis model)
- [ ] Implement conversation history analysis for consistent behavior
- [ ] Add user preferences for behavior intensity
- [ ] Performance optimization for real-time processing
