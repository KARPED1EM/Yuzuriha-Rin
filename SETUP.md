# Setup Guide

Quick start guide for running the Rie Kugimiya virtual character system.

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- An API key from OpenAI, Anthropic, or another compatible LLM provider

## Installation

### 1. Clone the repository

```bash
cd Rie_Kugimiya
```

### 2. Install dependencies

**Using pip:**
```bash
pip install -r requirements.txt
```

**Using uv (recommended):**
```bash
uv sync
```

### 3. (Optional) Install development dependencies

For running tests and development:

```bash
pip install pytest pytest-asyncio httpx
```

## Running the Application

### Option 1: Direct Python

```bash
python -m src.api.main
```

### Option 2: Using uvicorn

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The application will start on `http://localhost:8000`

## First Time Setup

1. **Open your browser** and navigate to `http://localhost:8000`

2. **Configure LLM Provider**:
   - Select your provider (OpenAI, Anthropic, or Custom)
   - Enter your API key
   - (Optional) Customize the base URL for custom providers
   - Select your model (e.g., `gpt-3.5-turbo` for OpenAI)

3. **Customize Character**:
   - Edit the system prompt to define the character's personality
   - Set the character name (default: "Rie")

4. **Save Configuration**:
   - Click "Save & Start Chat"
   - Your settings will be saved to browser localStorage

5. **Start Chatting**:
   - Type your message and press Enter or click Send
   - Watch the natural message behaviors:
     - Message segmentation (multiple bubbles)
     - Typing indicators
     - Natural pauses between messages
     - Occasional typos and corrections

## Configuration Options

### Behavior Settings

The system supports customizable behavior through API requests. You can adjust:

- **Segmentation**: Enable/disable message splitting
- **Typo Injection**: Enable/disable typos (default 8% rate)
- **Recall Behavior**: Enable/disable typo corrections (default 40% recall rate)
- **Emotion Detection**: Enable/disable emotion-based behavior adjustments

### Example: Custom Behavior via API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "llm_config": {
      "provider": "openai",
      "api_key": "your-api-key",
      "model": "gpt-3.5-turbo",
      "system_prompt": "You are Rie..."
    },
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "behavior_settings": {
      "enable_segmentation": true,
      "enable_typo": true,
      "enable_recall": true,
      "base_typo_rate": 0.1,
      "typo_recall_rate": 0.5
    }
  }'
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_behavior.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you're running from the project root directory and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: API requests failing

**Solution**: Check that:
1. Your API key is valid
2. The base URL is correct (for custom providers)
3. You have internet connection
4. The model name is spelled correctly

### Issue: Frontend not loading

**Solution**:
1. Check that the backend is running on port 8000
2. Clear browser cache
3. Check browser console for errors

### Issue: No typing animation

**Solution**: Make sure you're using a modern browser (Chrome, Firefox, Safari, Edge). JavaScript must be enabled.

## Development

### Project Structure

```
Rie_Kugimiya/
├── src/
│   ├── api/              # FastAPI backend
│   │   ├── main.py       # Application entry
│   │   ├── routes.py     # API endpoints
│   │   ├── schemas.py    # Request/response models
│   │   └── llm_client.py # LLM provider clients
│   ├── behavior/         # Message behavior system
│   │   ├── coordinator.py # Main orchestrator
│   │   ├── segmenter.py  # Message segmentation
│   │   ├── emotion.py    # Emotion detection
│   │   ├── typo.py       # Typo injection
│   │   ├── pause.py      # Pause prediction
│   │   └── models.py     # Data models
│   └── utils/            # Utilities
│       └── config.py     # App configuration
├── frontend/             # Web interface
│   ├── index.html        # Main page
│   ├── chat.js           # Chat logic
│   └── styles.css        # Styling
├── tests/                # Test suite
│   └── test_behavior.py  # Behavior system tests
├── data/                 # Data storage (create as needed)
│   └── models/           # ML model checkpoints
├── README.md             # Project overview
├── IMPLEMENTATION.md     # Technical documentation
└── SETUP.md             # This file
```

### Adding New Features

1. **Backend**: Add routes in `src/api/routes.py`
2. **Behavior**: Extend components in `src/behavior/`
3. **Frontend**: Update `frontend/chat.js` and `frontend/styles.css`
4. **Tests**: Add tests in `tests/`

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to classes and functions
- Keep functions focused and modular

## Support

For issues and questions:
1. Check the [Implementation Guide](IMPLEMENTATION.md)
2. Review existing issues on GitHub
3. Create a new issue with details about your problem

## License

MIT License - See LICENSE file for details
