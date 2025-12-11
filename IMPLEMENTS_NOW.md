# Yuzuriha Rin 架构文档

> 最后更新: 2025-12-12
> 架构版本: 2.0 (重构完成)

---

## 📐 架构概览

本项目采用**分层架构设计**，遵循领域驱动设计(DDD)和清洁架构(Clean Architecture)原则。

### 核心原则

1. **职责分离**: 每个模块只负责一个明确的职责
2. **依赖倒置**: 高层模块不依赖低层模块，都依赖抽象
3. **接口隔离**: 使用Repository模式和Service层隔离业务逻辑
4. **单一数据源**: 数据库和配置集中管理
5. **事件驱动**: WebSocket消息作为事件，驱动UI更新

---

## 🗂️ 目录结构

### 最终架构

```
src/
├── core/                           # 核心领域层
│   ├── models/                     # 领域模型
│   │   ├── message.py              # 消息模型 (Message, MessageType, WSMessage)
│   │   ├── character.py            # 角色模型 (Character)
│   │   ├── session.py              # 会话模型 (Session)
│   │   └── __init__.py
│   └── config/                     # 配置管理
│       ├── settings.py             # 所有配置类 (AppConfig, LLMDefaults等)
│       └── __init__.py             # 统一导出
│
├── infrastructure/                 # 基础设施层
│   ├── database/                   # 数据持久化
│   │   ├── connection.py           # 数据库连接管理
│   │   └── repositories/           # 仓储层
│   │       ├── base.py             # BaseRepository (抽象基类)
│   │       ├── message_repo.py     # MessageRepository
│   │       ├── character_repo.py   # CharacterRepository
│   │       ├── session_repo.py     # SessionRepository
│   │       ├── config_repo.py      # ConfigRepository
│   │       └── __init__.py
│   ├── network/                    # 网络通信
│   │   ├── websocket_manager.py    # WebSocket连接管理
│   │   ├── port_manager.py         # 端口管理
│   │   └── __init__.py
│   └── utils/                      # 基础设施工具
│       └── logger.py               # 日志工具
│
├── services/                       # 业务逻辑层
│   ├── messaging/                  # 消息服务
│   │   ├── message_service.py      # 消息CRUD、撤回、时间轴等
│   │   └── __init__.py
│   ├── character/                  # 角色服务
│   │   ├── character_service.py    # 角色管理、内置角色初始化
│   │   └── __init__.py
│   ├── session/                    # 会话服务 (待实现)
│   │   └── __init__.py
│   ├── config/                     # 配置服务
│   │   ├── config_service.py       # 应用配置、用户设置
│   │   └── __init__.py
│   └── ai/                         # AI服务
│       ├── llm_client.py           # LLM客户端
│       ├── rin_client.py           # Rin AI客户端
│       └── __init__.py
│
├── behavior/                       # 行为引擎 (独立模块)
│   ├── models.py                   # 行为模型 (PlaybackAction等)
│   ├── coordinator.py              # 行为协调器
│   ├── timeline.py                 # 时间轴构建器
│   ├── segmenter.py                # 智能分段
│   ├── emotion.py                  # 情绪检测
│   ├── typo.py                     # 错别字注入
│   ├── pause.py                    # 停顿预测
│   ├── same_pinyin_finder.py       # 同音字查找
│   └── __init__.py
│
├── api/                            # API层/表示层
│   ├── main.py                     # FastAPI应用入口
│   ├── routes.py                   # REST API路由
│   ├── ws_routes.py                # WebSocket路由
│   ├── schemas.py                  # API数据模型 (DTO)
│   ├── dependencies.py             # 依赖注入 (新增)
│   └── __init__.py
│
├── config.py                       # 向后兼容导入 (from src.core.config import *)
└── __init__.py
```

### 层级职责

| 层级 | 职责 | 依赖关系 |
|------|------|---------|
| **Core** | 定义领域模型和配置 | 不依赖任何层 |
| **Infrastructure** | 数据访问、网络通信 | 依赖 Core |
| **Services** | 业务逻辑编排 | 依赖 Infrastructure + Core |
| **Behavior** | 行为模拟引擎 | 独立模块 |
| **API** | HTTP/WebSocket接口 | 依赖 Services |

---

## 🔌 核心接口使用指南

### 1. 配置 (Core Config)

**导入方式**:
```python
from src.core.config import (
    app_config,          # 应用配置
    database_config,     # 数据库配置
    websocket_config,    # WebSocket配置
    llm_defaults,        # LLM默认配置
    behavior_defaults,   # 行为系统配置
    typing_state_defaults, # 输入状态配置
)
```

**使用示例**:
```python
# 获取数据库路径
db_path = database_config.path  # "data/rin_app.db"

# 获取WebSocket配置
host = websocket_config.host
port = websocket_config.port

# 获取LLM配置
provider = llm_defaults.provider  # "deepseek"
model = llm_defaults.model_deepseek  # "deepseek-chat"
```

### 2. 模型 (Core Models)

**导入方式**:
```python
from src.core.models import (
    Message,         # 消息模型
    MessageType,     # 消息类型枚举
    Character,       # 角色模型
    Session,         # 会话模型
)
```

**使用示例**:
```python
# 创建消息
message = Message(
    id="msg-123",
    session_id="session-1",
    sender_id="user",
    type=MessageType.TEXT,
    content="Hello",
    metadata={},
    is_recalled=False,
    is_read=False,
    timestamp=1234567890.0
)

# 创建角色
character = Character(
    id="char-1",
    name="Rin",
    avatar="/static/images/avatar/rin.webp",
    persona="...",
    is_builtin=True
)
```

### 3. Repository (Infrastructure)

**导入方式**:
```python
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.database.repositories import (
    MessageRepository,
    CharacterRepository,
    SessionRepository,
    ConfigRepository
)
```

**使用示例**:
```python
# 1. 创建数据库连接
conn = DatabaseConnection("data/rin_app.db")

# 2. 创建Repository
message_repo = MessageRepository(conn)

# 3. 使用Repository
await message_repo.create(message)
messages = await message_repo.get_by_session("session-1")
await message_repo.update_recalled_status("msg-123", True)
```

**Repository 接口** (所有Repository都实现):
```python
async def get_by_id(id: str) -> Optional[T]
async def get_all() -> List[T]
async def create(entity: T) -> bool
async def update(entity: T) -> bool
async def delete(id: str) -> bool
```

**专有方法**:
- `MessageRepository`: `get_by_session()`, `update_recalled_status()`, `delete_by_session()`
- `CharacterRepository`: 无额外方法
- `SessionRepository`: `get_by_character()`, `get_active_session()`, `set_active_session()`
- `ConfigRepository`: `get_config()`, `set_config()`, `get_user_avatar()`, `set_user_avatar()`

### 4. Service (Services)

**导入方式**:
```python
from src.services.messaging.message_service import MessageService
from src.services.character.character_service import CharacterService
from src.services.config.config_service import ConfigService
```

**使用示例**:
```python
# 1. 创建Service (需要注入Repository)
message_service = MessageService(message_repo)
character_service = CharacterService(
    character_repo,
    session_repo,
    message_service
)

# 2. 使用Service
# 发送消息
message = await message_service.send_message(
    session_id="session-1",
    sender_id="user",
    message_type=MessageType.TEXT,
    content="Hello"
)

# 撤回消息
recall_msg = await message_service.recall_message(
    session_id="session-1",
    message_id="msg-123",
    timestamp=1234567890.0,
    recalled_by="user"
)

# 创建角色
character = await character_service.create_character(
    name="New Character",
    avatar="/static/avatar.png",
    persona="A friendly assistant"
)
```

**Service 接口**:

**MessageService**:
- `send_message()` - 发送消息
- `recall_message()` - 撤回消息
- `create_session()` - 创建会话初始消息
- `delete_session()` - 删除会话所有消息
- `get_message()` - 获取单条消息
- `get_messages()` - 获取会话消息列表
- `set_typing_state()` - 设置输入状态
- `set_emotion_state()` - 设置情绪状态

**CharacterService**:
- `initialize_builtin_characters()` - 初始化内置角色
- `create_character()` - 创建角色
- `get_character()` - 获取角色
- `get_all_characters()` - 获取所有角色
- `update_character()` - 更新角色
- `delete_character()` - 删除角色
- `get_character_session()` - 获取角色对应的会话
- `switch_active_session()` - 切换活动会话
- `recreate_session()` - 重建会话

**ConfigService**:
- `get_config()` - 获取单个配置
- `get_all_config()` - 获取所有配置
- `set_config()` - 批量设置配置
- `get_user_avatar()` - 获取用户头像
- `set_user_avatar()` - 设置用户头像
- `delete_user_avatar()` - 删除用户头像
- `compute_hash()` - 计算数据hash (用于同步)

### 5. WebSocket (Infrastructure)

**导入方式**:
```python
from src.infrastructure.network.websocket_manager import WebSocketManager
```

**使用示例**:
```python
# 1. 创建WebSocket管理器
ws_manager = WebSocketManager()

# 2. 连接管理
await ws_manager.connect(websocket, "session-1", "user")
ws_manager.disconnect(websocket, "session-1")

# 3. 消息发送
await ws_manager.send_to_conversation("session-1", {
    "type": "message",
    "data": {...}
})

await ws_manager.send_to_websocket(websocket, {...})

# 4. 调试模式
ws_manager.enable_debug_mode(websocket, "session-1")
await ws_manager.broadcast_debug_log({...})
```

### 6. 行为引擎 (Behavior)

**导入方式**:
```python
from src.behavior.coordinator import BehaviorCoordinator
from src.behavior.models import PlaybackAction, BehaviorConfig
```

**使用示例**:
```python
# 1. 创建行为协调器
coordinator = BehaviorCoordinator()

# 2. 生成行为时间轴
timeline = coordinator.process_message(
    text="你好！今天天气真好。",
    emotion_map={"happy": 0.8}
)

# timeline 是 List[PlaybackAction]
# PlaybackAction包含: type, timestamp, text, message_id等

# 3. 执行时间轴 (通常在RinClient中)
for action in timeline:
    if action.type == "typing_start":
        await set_typing_state(True)
    elif action.type == "send":
        await send_message(action.text)
    # ...
```

---

## 🔄 数据流示例

### 用户发送消息流程

```
Frontend                 API Layer                Service Layer           Infrastructure
   │                        │                        │                        │
   │  WebSocket: message    │                        │                        │
   ├───────────────────────>│                        │                        │
   │                        │ ws_routes.py           │                        │
   │                        │ handle_user_message()  │                        │
   │                        ├───────────────────────>│                        │
   │                        │                        │ MessageService         │
   │                        │                        │ .send_message()        │
   │                        │                        ├───────────────────────>│
   │                        │                        │                        │ MessageRepository
   │                        │                        │                        │ .create()
   │                        │                        │                        │
   │                        │  Broadcast to all      │<───────────────────────┤
   │<───────────────────────┤                        │                        │
   │  WebSocket: message    │                        │                        │
   │  event                 │                        │                        │
```

### 初始化服务流程

```
1. api/main.py 启动
   └─> 导入 api/routes.py
       └─> routes.py 定义 initialize_services()
           └─> 创建 DatabaseConnection
           └─> 创建 Repositories
           └─> 创建 Services
           └─> 调用 character_service.initialize_builtin_characters()
               └─> 检查内置角色是否存在
               └─> 不存在则创建Rin和Abai
               └─> 创建对应Session
               └─> 调用 message_service.create_session()
                   └─> 创建初始系统消息
```

---

## 🎯 最佳实践

### 1. 永远通过Service层操作数据

**❌ 错误做法**:
```python
# 直接使用Repository
message_repo = MessageRepository(conn)
await message_repo.create(message)
```

**✅ 正确做法**:
```python
# 通过Service
message_service = MessageService(message_repo)
await message_service.send_message(...)  # Service会处理业务逻辑
```

### 2. 配置集中管理

**❌ 错误做法**:
```python
DB_PATH = "data/db.sqlite"  # 硬编码
```

**✅ 正确做法**:
```python
from src.core.config import database_config
db_path = database_config.path  # 统一配置
```

### 3. 使用绝对导入

**❌ 错误做法**:
```python
from ..database.manager import DatabaseManager  # 相对导入
```

**✅ 正确做法**:
```python
from src.infrastructure.database.repositories import MessageRepository  # 绝对导入
```

### 4. 会话与角色强制一对一

**必须遵守**:
```python
# Session必须关联Character
session = Session(
    id="session-1",
    character_id="char-1",  # 必须存在
    is_active=True
)

# 获取会话对应的角色
character = await character_service.get_character(session.character_id)
```

---

## 📦 向后兼容

为了不破坏现有代码,在旧位置提供了兼容导入:

```python
# 旧代码仍然可以工作
from src.config import app_config  # 自动重定向到 src.core.config

# 但推荐使用新路径
from src.core.config import app_config
```

---

## 🚀 启动应用

### 开发模式

```bash
python run.py
```

或

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📚 扩展指南

### 添加新的Repository

1. 在 `src/infrastructure/database/repositories/` 创建新文件
2. 继承 `BaseRepository[T]`
3. 实现抽象方法
4. 在 `__init__.py` 中导出

### 添加新的Service

1. 在 `src/services/` 创建新目录
2. 创建 service.py 文件
3. 在 `__init__.py` 中定义服务
4. 注入需要的Repositories

### 添加新的API路由

1. 在 `src/api/` 创建新路由文件 (如 `src/api/rest/xxx.py`)
2. 在 `main.py` 中注册路由
3. 使用 `initialize_services()` 获取服务实例

---

**架构负责人**: Claude (Sonnet 4.5)
**文档版本**: 2.0
**最后更新**: 2025-12-12
