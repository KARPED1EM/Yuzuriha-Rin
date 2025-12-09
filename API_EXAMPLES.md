# API Examples

This document provides practical examples of using the Rie Kugimiya API.

## Basic Chat Request

### Minimal Configuration

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "llm_config": {
      "provider": "openai",
      "api_key": "your-api-key-here",
      "model": "gpt-3.5-turbo",
      "system_prompt": "You are Rie Kugimiya, a cute and sassy character."
    },
    "messages": [
      {"role": "user", "content": "你好！"}
    ]
  }'
```

### With Behavior Settings

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "llm_config": {
      "provider": "openai",
      "api_key": "your-api-key-here",
      "model": "gpt-3.5-turbo",
      "system_prompt": "You are Rie."
    },
    "messages": [
      {"role": "user", "content": "今天天气怎么样？"}
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

## Provider-Specific Examples

### OpenAI

```python
import httpx
import asyncio

async def chat_with_openai():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "llm_config": {
                    "provider": "openai",
                    "api_key": "sk-...",
                    "model": "gpt-3.5-turbo",
                    "system_prompt": "You are a helpful assistant."
                },
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        return response.json()

result = asyncio.run(chat_with_openai())
print(result)
```

### Anthropic (Claude)

```python
async def chat_with_claude():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "llm_config": {
                    "provider": "anthropic",
                    "api_key": "sk-ant-...",
                    "model": "claude-3-5-sonnet-20241022",
                    "system_prompt": "You are Rie, a virtual character."
                },
                "messages": [
                    {"role": "user", "content": "你好！"}
                ]
            }
        )
        return response.json()

result = asyncio.run(chat_with_claude())
```

### Custom OpenAI-Compatible API

```python
async def chat_with_custom():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={
                "llm_config": {
                    "provider": "custom",
                    "api_key": "your-key",
                    "base_url": "https://your-api.com/v1",
                    "model": "your-model-name",
                    "system_prompt": "You are Rie."
                },
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        return response.json()
```

## Response Format

### Typical Response

```json
{
  "actions": [
    {
      "type": "typing_start",
      "delay": 0.0,
      "text": null,
      "typing_speed": null,
      "metadata": null
    },
    {
      "type": "send",
      "delay": 0.1,
      "text": "你好呀！",
      "typing_speed": 0.04,
      "metadata": {
        "has_typo": false,
        "is_recalled": false
      }
    },
    {
      "type": "typing_end",
      "delay": 0.0,
      "text": null,
      "typing_speed": null,
      "metadata": null
    },
    {
      "type": "pause",
      "delay": 0.8,
      "text": null,
      "typing_speed": null,
      "metadata": null
    },
    {
      "type": "typing_start",
      "delay": 0.0,
      "text": null,
      "typing_speed": null,
      "metadata": null
    },
    {
      "type": "send",
      "delay": 0.1,
      "text": "今天过得怎么样？",
      "typing_speed": 0.045,
      "metadata": {
        "has_typo": false,
        "is_recalled": false
      }
    },
    {
      "type": "typing_end",
      "delay": 0.0,
      "text": null,
      "typing_speed": null,
      "metadata": null
    }
  ],
  "raw_response": "你好呀！今天过得怎么样？",
  "metadata": {
    "emotion": "happy",
    "segment_count": 2
  }
}
```

### Response with Typo and Recall

```json
{
  "actions": [
    {
      "type": "typing_start",
      "delay": 0.0
    },
    {
      "type": "recall",
      "delay": 0.1,
      "text": "你号！",
      "typing_speed": 0.05,
      "metadata": {
        "has_typo": true,
        "is_recalled": true
      }
    },
    {
      "type": "typing_end",
      "delay": 0.0
    },
    {
      "type": "pause",
      "delay": 0.8
    },
    {
      "type": "typing_start",
      "delay": 0.0
    },
    {
      "type": "send",
      "delay": 0.1,
      "text": "你好！",
      "typing_speed": 0.05,
      "metadata": {
        "has_typo": false,
        "is_recalled": false
      }
    },
    {
      "type": "typing_end",
      "delay": 0.0
    }
  ],
  "raw_response": "你好！",
  "metadata": {
    "emotion": "neutral",
    "segment_count": 2
  }
}
```

## Behavior Configuration

### Disable All Behaviors (Direct LLM Output)

```json
{
  "llm_config": {...},
  "messages": [...],
  "behavior_settings": {
    "enable_segmentation": false,
    "enable_typo": false,
    "enable_recall": false,
    "enable_emotion_detection": false
  }
}
```

### High Typo Rate (Testing)

```json
{
  "llm_config": {...},
  "messages": [...],
  "behavior_settings": {
    "enable_typo": true,
    "base_typo_rate": 0.3,
    "typo_recall_rate": 0.8
  }
}
```

### Conservative Behavior

```json
{
  "llm_config": {...},
  "messages": [...],
  "behavior_settings": {
    "enable_segmentation": true,
    "enable_typo": true,
    "enable_recall": true,
    "base_typo_rate": 0.03,
    "typo_recall_rate": 0.2
  }
}
```

## Error Handling

### Invalid API Key

```json
{
  "detail": "HTTP error: 401"
}
```

### Invalid Model Name

```json
{
  "detail": "HTTP error: 404"
}
```

### Missing Required Fields

```json
{
  "detail": [
    {
      "loc": ["body", "llm_config", "api_key"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok"
}
```

## JavaScript Frontend Example

```javascript
async function sendMessage(text) {
  const config = {
    provider: "openai",
    api_key: "sk-...",
    model: "gpt-3.5-turbo",
    system_prompt: "You are Rie."
  };

  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      llm_config: config,
      messages: [
        { role: 'user', content: text }
      ]
    })
  });

  const data = await response.json();

  // Play actions sequentially
  for (const action of data.actions) {
    if (action.delay > 0) {
      await sleep(action.delay * 1000);
    }

    switch (action.type) {
      case 'typing_start':
        showTypingIndicator();
        break;
      case 'typing_end':
        hideTypingIndicator();
        break;
      case 'send':
        await displayMessageWithTyping(action.text, action.typing_speed);
        break;
      case 'recall':
        markLastAsRecalled();
        await displayMessageWithTyping(action.text, action.typing_speed);
        break;
    }
  }
}
```

## Batch Processing Example

```python
async def process_multiple_messages():
    messages = [
        "你好！",
        "今天天气真好",
        "你喜欢什么？"
    ]

    async with httpx.AsyncClient() as client:
        tasks = []
        for msg in messages:
            task = client.post(
                "http://localhost:8000/api/chat",
                json={
                    "llm_config": {...},
                    "messages": [{"role": "user", "content": msg}]
                }
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

## Tips

1. **Rate Limiting**: Be mindful of your LLM provider's rate limits
2. **Error Handling**: Always handle potential API errors
3. **Caching**: Consider caching config to avoid repeated API calls
4. **Timeouts**: Set appropriate timeouts for long-running requests
5. **Behavior Tuning**: Adjust behavior settings based on use case
