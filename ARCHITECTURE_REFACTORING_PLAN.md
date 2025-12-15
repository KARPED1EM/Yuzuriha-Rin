# 架构重构完整计划 Complete Architecture Refactoring Plan

## 📋 执行摘要 Executive Summary

基于你的反馈，我对项目进行了深入的架构审查，发现了以下**严重违反分层架构原则**的问题。本文档提供完整的重构计划，确保项目**完全遵循分层架构 + 轻量级 DDD**，并为桌面应用打包做好准备。

---

## 🔍 深度问题分析 In-Depth Issue Analysis

### 问题 1：image_alter.json 位置和用途 ⚠️ 已确认

**用途分析：**
通过代码审查，`image_alter.json` 是一个**图片文本描述映射文件**，用于：
- 为头像和表情包提供文本描述（用于 LLM 理解图片内容）
- 支持无障碍访问
- 在 LLM 历史记录中提供图片的文本替代

**当前使用位置：**
1. `src/utils/image_alter.py` - 读取和缓存描述
2. `src/services/session/session_client.py` - 获取图片描述用于 LLM 上下文
3. `src/services/tools/tool_service.py` - 工具服务获取头像描述
4. `tools/sticker_manager/sticker_manager.py` - GUI 工具编辑描述

**性质判定：** **应用配置文件（Application Configuration）**
- 不是运行时数据（不会被程序修改，除非通过专门的管理工具）
- 不是用户数据
- 属于应用资源配置

**正确位置：** `assets/config/image_descriptions.json` ✅

**理由：**
1. 这是只读的应用配置，不是运行时数据
2. 与 stickers 等资源关联紧密，应该在 assets/ 下
3. 重命名为 `image_descriptions.json` 更语义化

---

### 问题 2：API 路由文件命名混乱 🔴 严重问题

**当前命名：**
```
src/api/
├── routes.py              # 普通 HTTP REST API
├── ws_routes.py           # 每个会话的 WebSocket
└── ws_global_routes.py    # 全局 WebSocket
```

**问题：**
1. `routes.py` 太泛化，无法从名字看出是 REST API
2. `ws_routes.py` vs `ws_global_routes.py` - 需要看代码才能理解区别
3. 不符合语义化命名原则

**推荐命名方案 A（REST + WebSocket 分离）：**
```
src/api/
├── http_routes.py         # HTTP REST API（字符、会话、配置等）
├── websocket_session.py   # 每会话 WebSocket（聊天消息）
└── websocket_global.py    # 全局 WebSocket（日志、系统事件）
```

**推荐命名方案 B（业务领域分离）：**
```
src/api/
├── character_routes.py    # 角色管理 REST API
├── config_routes.py       # 配置管理 REST API  
├── session_routes.py      # 会话管理 REST API
├── websocket_chat.py      # 聊天 WebSocket（每会话）
└── websocket_system.py    # 系统 WebSocket（全局日志）
```

**推荐方案：方案 A** - 简单清晰，符合当前项目规模

---

### 问题 3：服务层依赖具体实现 🚨 **零容忍问题**

通过代码审查，发现以下**严重违反分层架构**的依赖：

#### 违规 1：服务层直接依赖 API 层 schemas

**违规代码：**
```python
# src/services/llm/llm_client.py:10
from src.api.schemas import ChatMessage, LLMConfig

# src/services/session/session_client.py:6
from src.api.schemas import LLMConfig, ChatMessage
```

**问题：**
- 服务层（Service Layer）依赖 API 层（Presentation Layer）
- **严重违反分层架构**：高层模块依赖低层模块

**正确做法：**
schemas 应该属于 **Domain Layer** 或 **Service Layer**，不应该在 API 层

**解决方案：**
```
移动：
src/api/schemas.py → src/core/schemas.py

或者细分：
src/api/schemas.py → src/core/models/schemas.py
                  → src/services/llm/schemas.py（LLM 专用）
```

#### 违规 2：服务层直接依赖基础设施层具体实现

**违规代码：**
```python
# src/services/config/config_service.py:3
from src.infrastructure.database.repositories.config_repo import ConfigRepository

# src/services/messaging/message_service.py:10
from src.infrastructure.database.repositories.message_repo import MessageRepository

# src/services/character/character_service.py:6-7
from src.infrastructure.database.repositories.character_repo import CharacterRepository
from src.infrastructure.database.repositories.session_repo import SessionRepository
```

**问题：**
- 服务层直接依赖仓储的**具体实现**
- 应该依赖**抽象接口**，而不是具体类

**当前状态：** ❌ 有 `BaseRepository` 基类，但服务层仍然依赖具体实现

**正确做法（依赖倒置原则）：**

```python
# 1. 定义接口（在 core/ 或 services/interfaces/）
# src/core/interfaces/repositories.py

from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.models.character import Character
from src.core.models.message import Message

class ICharacterRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Character]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Character]:
        pass
    
    @abstractmethod
    async def create(self, character: Character) -> bool:
        pass

class IMessageRepository(ABC):
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> List[Message]:
        pass
    # ... 其他方法

# 2. 服务层依赖接口
# src/services/character/character_service.py

from src.core.interfaces.repositories import ICharacterRepository, ISessionRepository

class CharacterService:
    def __init__(
        self,
        character_repo: ICharacterRepository,  # 依赖抽象
        session_repo: ISessionRepository,       # 依赖抽象
        ...
    ):
        self.character_repo = character_repo
        self.session_repo = session_repo

# 3. 具体实现在 infrastructure/
# src/infrastructure/database/repositories/character_repo.py

from src.core.interfaces.repositories import ICharacterRepository

class CharacterRepository(ICharacterRepository):  # 实现接口
    # 具体实现
    pass

# 4. 依赖注入在 API 层
# src/api/http_routes.py

from src.core.interfaces.repositories import ICharacterRepository
from src.infrastructure.database.repositories.character_repo import CharacterRepository

# 创建具体实现
character_repo: ICharacterRepository = CharacterRepository(conn_mgr)
# 注入到服务
character_service = CharacterService(character_repo, ...)
```

**收益：**
- ✅ 服务层完全独立于基础设施实现
- ✅ 可以轻松替换数据库（SQLite → PostgreSQL）
- ✅ 易于单元测试（Mock 接口）
- ✅ 符合 SOLID 原则

#### 违规 3：日志工具的依赖问题

**违规代码：**
```python
# 多个服务层文件
from src.infrastructure.utils.logger import unified_logger, LogCategory
```

**问题分析：**
- 日志是横切关注点（Cross-cutting Concern）
- 但当前实现在 infrastructure 层，导致服务层依赖基础设施

**解决方案 1（推荐）：** 日志接口在 core，实现在 infrastructure
```python
# src/core/interfaces/logger.py
from abc import ABC, abstractmethod

class ILogger(ABC):
    @abstractmethod
    def log(self, level: str, message: str, category: str = None):
        pass

# src/infrastructure/utils/logger.py
from src.core.interfaces.logger import ILogger

class UnifiedLogger(ILogger):
    def log(self, level: str, message: str, category: str = None):
        # 具体实现
        pass

# 服务层使用
from src.core.interfaces.logger import ILogger

class SomeService:
    def __init__(self, logger: ILogger):
        self.logger = logger
```

**解决方案 2（简单）：** 日志工具移到 core/utils/
```
移动：
src/infrastructure/utils/logger.py → src/core/utils/logger.py
```

理由：日志是应用核心功能，不是外部基础设施

---

### 问题 4：桌面应用打包准备 🖥️

你提到要用 **pywebview + pyinstaller** 打包为桌面应用。

**pywebview 架构分析：**
- pywebview 提供原生窗口包装 Web 应用
- 需要一个入口脚本启动 FastAPI + pywebview
- 静态资源需要正确路径

**推荐文件组织：**

```
Yuzuriha-Rin/
├── src/
│   ├── desktop/                    # 新增：桌面应用模块
│   │   ├── __init__.py
│   │   ├── main.py                 # 桌面应用入口
│   │   ├── window.py               # pywebview 窗口管理
│   │   └── config.py               # 桌面应用配置
│   ├── frontend/                   # Web 前端（pywebview 加载）
│   ├── api/
│   └── ...
├── desktop.py                      # 桌面启动入口（根目录）
├── run.py                          # Web 服务启动入口
└── build/                          # 打包脚本和资源
    ├── pyinstaller/
    │   ├── desktop.spec            # PyInstaller 配置
    │   ├── hooks/                  # 自定义 hooks
    │   └── resources/              # 打包资源
    └── icons/
        ├── app.ico                 # Windows 图标
        └── app.icns                # macOS 图标
```

**desktop.py 示例：**

```python
"""
Desktop application entry point using pywebview
"""
import sys
import threading
import webview
import uvicorn
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.main import app
from src.infrastructure.network.port_manager import PortManager
from src.core.config import websocket_config


def start_server(port: int, host: str):
    """Start FastAPI server in background thread"""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        ws_ping_interval=websocket_config.ping_interval,
        ws_ping_timeout=websocket_config.ping_timeout,
    )


def main():
    """Main entry point for desktop app"""
    # Initialize port manager
    PortManager.initialize(start_port=8000, host="127.0.0.1")
    port_manager = PortManager.get_instance()
    
    port = port_manager.get_port()
    host = port_manager.get_host()
    url = f"http://{host}:{port}"
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=start_server,
        args=(port, host),
        daemon=True
    )
    server_thread.start()
    
    # Create and show pywebview window
    window = webview.create_window(
        title="Yuzuriha Rin - 虚拟角色对话系统",
        url=url,
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600),
    )
    
    webview.start(debug=False)


if __name__ == "__main__":
    main()
```

**desktop.spec (PyInstaller) 示例：**

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/frontend', 'src/frontend'),
        ('assets', 'assets'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=['build/pyinstaller/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YuzurihaRin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='build/icons/app.ico',
)
```

**路径处理注意事项：**

PyInstaller 打包后，资源路径会改变。需要处理：

```python
# src/core/utils/paths.py
"""
Path utilities for handling development vs packaged application
"""
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Get base path for application resources
    
    In development: project root
    In packaged app: _MEIPASS (PyInstaller temp folder)
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in development
        return Path(__file__).parent.parent.parent


def get_asset_path(relative_path: str) -> Path:
    """Get absolute path to an asset file"""
    return get_base_path() / relative_path


def get_data_path(relative_path: str) -> Path:
    """Get absolute path to a data file"""
    # In packaged app, data should be in user's home directory
    if getattr(sys, 'frozen', False):
        from pathlib import Path
        app_data = Path.home() / '.yuzuriha-rin'
        app_data.mkdir(exist_ok=True)
        return app_data / relative_path
    else:
        return get_base_path() / 'data' / relative_path
```

然后更新所有路径引用：

```python
# 修改前
frontend_dir = os.path.join(os.path.dirname(__file__), "../../frontend")

# 修改后
from src.core.utils.paths import get_asset_path
frontend_dir = get_asset_path("src/frontend")
```

---

## 📊 完整重构待办清单 Complete TODO List

### 阶段 1：紧急修复（分层架构违规）🚨 优先级：P0

#### 1.1 修复服务层依赖 API 层（schemas）

- [ ] **任务 1.1.1：** 移动 schemas 到正确位置
  - [ ] 创建 `src/core/schemas.py`
  - [ ] 移动 `LLMConfig`, `ChatMessage` 到 `src/core/schemas.py`
  - [ ] 保留 API 特定的 schemas 在 `src/api/schemas.py`（如 `ChatRequest`, `ChatResponse`）
  - [ ] 更新所有导入引用
  
- [ ] **任务 1.1.2：** 更新服务层导入
  ```python
  # 修改前
  from src.api.schemas import ChatMessage, LLMConfig
  
  # 修改后
  from src.core.schemas import ChatMessage, LLMConfig
  ```
  
  **影响文件：**
  - `src/services/llm/llm_client.py`
  - `src/services/session/session_client.py`

#### 1.2 引入仓储接口（依赖倒置）

- [ ] **任务 1.2.1：** 创建仓储接口
  - [ ] 创建 `src/core/interfaces/`
  - [ ] 创建 `src/core/interfaces/__init__.py`
  - [ ] 创建 `src/core/interfaces/repositories.py`
  - [ ] 定义所有仓储接口：
    - `ICharacterRepository`
    - `IMessageRepository`
    - `ISessionRepository`
    - `IConfigRepository`

- [ ] **任务 1.2.2：** 让具体仓储实现接口
  ```python
  # src/infrastructure/database/repositories/character_repo.py
  from src.core.interfaces.repositories import ICharacterRepository
  
  class CharacterRepository(ICharacterRepository):
      # 实现所有抽象方法
      pass
  ```
  
  **影响文件：**
  - `src/infrastructure/database/repositories/character_repo.py`
  - `src/infrastructure/database/repositories/message_repo.py`
  - `src/infrastructure/database/repositories/session_repo.py`
  - `src/infrastructure/database/repositories/config_repo.py`

- [ ] **任务 1.2.3：** 更新服务层依赖抽象
  ```python
  # 修改前
  from src.infrastructure.database.repositories.character_repo import CharacterRepository
  
  # 修改后
  from src.core.interfaces.repositories import ICharacterRepository
  
  class CharacterService:
      def __init__(self, character_repo: ICharacterRepository, ...):
          pass
  ```
  
  **影响文件：**
  - `src/services/character/character_service.py`
  - `src/services/messaging/message_service.py`
  - `src/services/config/config_service.py`

- [ ] **任务 1.2.4：** 更新 API 层依赖注入
  **影响文件：**
  - `src/api/http_routes.py`（重命名后）
  - `src/api/websocket_session.py`（重命名后）
  - `src/api/websocket_global.py`（重命名后）

#### 1.3 修复日志依赖

- [ ] **任务 1.3.1：** 选择解决方案
  - [ ] 方案 A：创建日志接口 + 依赖注入
  - [ ] 方案 B：移动日志到 `src/core/utils/logger.py`
  
  **推荐：方案 B**（简单快速）

- [ ] **任务 1.3.2：** 执行移动（如果选方案 B）
  ```bash
  mkdir -p src/core/utils
  mv src/infrastructure/utils/logger.py src/core/utils/logger.py
  ```
  
  **影响文件：** 所有导入 logger 的文件（约 10+ 个）

---

### 阶段 2：目录和命名优化 📁 优先级：P1

#### 2.1 移动 frontend 到 src/

- [ ] **任务 2.1.1：** 移动目录
  ```bash
  mv frontend/ src/frontend/
  ```

- [ ] **任务 2.1.2：** 更新路径引用
  ```python
  # src/api/main.py:58-59
  # 修改前
  frontend_dir = os.path.join(os.path.dirname(__file__), "../../frontend")
  
  # 修改后
  frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
  ```

- [ ] **任务 2.1.3：** 测试前端访问

#### 2.2 重命名 models/ 为 scripts/ml_training/

- [ ] **任务 2.2.1：** 创建新目录并移动
  ```bash
  mkdir -p scripts/ml_training
  mv models/scripts/* scripts/ml_training/
  rm -rf models/
  ```

- [ ] **任务 2.2.2：** 更新文档引用

#### 2.3 重命名 API 路由文件

- [ ] **任务 2.3.1：** 重命名文件
  ```bash
  cd src/api/
  git mv routes.py http_routes.py
  git mv ws_routes.py websocket_session.py
  git mv ws_global_routes.py websocket_global.py
  ```

- [ ] **任务 2.3.2：** 更新 `src/api/main.py` 导入
  ```python
  # 修改前
  from src.api.ws_routes import router as ws_router
  from src.api.ws_global_routes import router as ws_global_router
  from src.api.routes import router as api_router
  
  # 修改后
  from src.api.websocket_session import router as ws_session_router
  from src.api.websocket_global import router as ws_global_router
  from src.api.http_routes import router as http_router
  ```

- [ ] **任务 2.3.3：** 更新所有内部导入引用

#### 2.4 重组 data/ 和创建 assets/

- [ ] **任务 2.4.1：** 创建新目录结构
  ```bash
  mkdir -p assets/stickers assets/jieba assets/config
  mkdir -p data/database
  mkdir -p archive
  ```

- [ ] **任务 2.4.2：** 移动文件
  ```bash
  # 移动表情包
  mv data/stickers/* assets/stickers/
  
  # 移动 jieba
  mv data/jieba/* assets/jieba/
  
  # 移动并重命名 image_alter.json
  mv data/image_alter.json assets/config/image_descriptions.json
  
  # 移动归档资源
  mv data/raw archive/raw
  
  # 移动数据库（如果存在）
  mv data/*.db data/database/ 2>/dev/null || true
  ```

- [ ] **任务 2.4.3：** 更新所有路径引用
  
  **影响文件：**
  - `src/api/http_routes.py`:33 - STICKER_BASE_DIR
  - `src/core/config/settings.py`:84 - database path
  - `src/utils/image_alter.py`:12 - image_descriptions.json path
  - 所有 jieba 引用
  - `tools/sticker_manager/sticker_manager.py` - 多处路径

- [ ] **任务 2.4.4：** 更新 `.gitignore`
  ```
  # 数据库文件
  data/database/*.db
  
  # 日志文件
  logs/
  
  # PyInstaller
  build/dist/
  build/build/
  *.spec
  ```

---

### 阶段 3：桌面应用准备 🖥️ 优先级：P2

#### 3.1 创建桌面应用模块

- [ ] **任务 3.1.1：** 创建目录结构
  ```bash
  mkdir -p src/desktop
  mkdir -p build/pyinstaller/hooks
  mkdir -p build/icons
  ```

- [ ] **任务 3.1.2：** 创建核心文件
  - [ ] `src/desktop/__init__.py`
  - [ ] `src/desktop/main.py` - 桌面应用主逻辑
  - [ ] `src/desktop/window.py` - pywebview 窗口管理
  - [ ] `src/desktop/config.py` - 桌面配置

- [ ] **任务 3.1.3：** 创建入口脚本
  - [ ] `desktop.py` - 根目录入口

#### 3.2 路径处理工具

- [ ] **任务 3.2.1：** 创建路径工具
  - [ ] `src/core/utils/__init__.py`
  - [ ] `src/core/utils/paths.py` - 开发/打包路径处理

- [ ] **任务 3.2.2：** 更新所有硬编码路径
  
  **需要更新的位置：**
  - `src/api/main.py` - frontend_dir
  - `src/api/http_routes.py` - STICKER_BASE_DIR
  - `src/core/config/settings.py` - database_config.path
  - `src/utils/image_alter.py` - _json_path
  - jieba 初始化代码

#### 3.3 PyInstaller 配置

- [ ] **任务 3.3.1：** 创建 spec 文件
  - [ ] `build/pyinstaller/desktop.spec`

- [ ] **任务 3.3.2：** 创建自定义 hooks（如需要）
  - [ ] `build/pyinstaller/hooks/hook-uvicorn.py`

- [ ] **任务 3.3.3：** 准备图标
  - [ ] Windows: `build/icons/app.ico`
  - [ ] macOS: `build/icons/app.icns`
  - [ ] Linux: `build/icons/app.png`

- [ ] **任务 3.3.4：** 创建打包脚本
  - [ ] `build/build_windows.bat`
  - [ ] `build/build_macos.sh`
  - [ ] `build/build_linux.sh`

#### 3.4 测试和验证

- [ ] **任务 3.4.1：** 开发模式测试
  ```bash
  python desktop.py
  ```

- [ ] **任务 3.4.2：** 打包测试
  ```bash
  pyinstaller build/pyinstaller/desktop.spec
  ```

- [ ] **任务 3.4.3：** 运行打包后的应用
  ```bash
  ./dist/YuzurihaRin  # Linux/macOS
  dist\YuzurihaRin.exe  # Windows
  ```

---

### 阶段 4：文档和配置更新 📝 优先级：P2

#### 4.1 更新 pyproject.toml

- [ ] **任务 4.1.1：** 添加桌面应用依赖
  ```toml
  dependencies = [
      # ... 现有依赖
      "pywebview>=5.0",
      "pyinstaller>=6.0",
  ]
  ```

- [ ] **任务 4.1.2：** 添加入口点
  ```toml
  [project.scripts]
  yuzuriha-rin-web = "run:main"
  yuzuriha-rin-desktop = "desktop:main"
  ```

#### 4.2 更新 README.md

- [ ] **任务 4.2.1：** 添加桌面应用说明
- [ ] **任务 4.2.2：** 更新目录结构说明
- [ ] **任务 4.2.3：** 添加打包说明

#### 4.3 更新架构文档

- [ ] **任务 4.3.1：** 更新 `ARCHITECTURE_ANALYSIS.md`
- [ ] **任务 4.3.2：** 更新 `ARCHITECTURE_DIAGRAMS.md`
- [ ] **任务 4.3.3：** 创建 `DESKTOP_BUILD_GUIDE.md`

---

## 📋 文件修改清单 File Change Checklist

### 需要修改的文件（按优先级）

#### P0 - 紧急（分层架构违规）

1. **创建新文件：**
   - [ ] `src/core/schemas.py` - 从 api/schemas.py 移动部分内容
   - [ ] `src/core/interfaces/__init__.py`
   - [ ] `src/core/interfaces/repositories.py` - 仓储接口定义

2. **修改文件：**
   - [ ] `src/api/schemas.py` - 移除 LLMConfig, ChatMessage
   - [ ] `src/services/llm/llm_client.py` - 更新导入
   - [ ] `src/services/session/session_client.py` - 更新导入
   - [ ] `src/infrastructure/database/repositories/base.py` - 移动到 core/interfaces/
   - [ ] `src/infrastructure/database/repositories/character_repo.py` - 实现接口
   - [ ] `src/infrastructure/database/repositories/message_repo.py` - 实现接口
   - [ ] `src/infrastructure/database/repositories/session_repo.py` - 实现接口
   - [ ] `src/infrastructure/database/repositories/config_repo.py` - 实现接口
   - [ ] `src/services/character/character_service.py` - 依赖抽象
   - [ ] `src/services/messaging/message_service.py` - 依赖抽象
   - [ ] `src/services/config/config_service.py` - 依赖抽象

3. **移动文件：**
   - [ ] `src/infrastructure/utils/logger.py` → `src/core/utils/logger.py`
   - [ ] 更新所有导入 logger 的文件（约 10+ 个）

#### P1 - 高优先级（命名和组织）

4. **移动目录：**
   - [ ] `frontend/` → `src/frontend/`
   - [ ] `models/scripts/` → `scripts/ml_training/`
   - [ ] `data/stickers/` → `assets/stickers/`
   - [ ] `data/jieba/` → `assets/jieba/`
   - [ ] `data/image_alter.json` → `assets/config/image_descriptions.json`
   - [ ] `data/raw/` → `archive/raw/`

5. **重命名文件：**
   - [ ] `src/api/routes.py` → `src/api/http_routes.py`
   - [ ] `src/api/ws_routes.py` → `src/api/websocket_session.py`
   - [ ] `src/api/ws_global_routes.py` → `src/api/websocket_global.py`

6. **修改导入引用：**
   - [ ] `src/api/main.py` - 更新路由导入和 frontend 路径
   - [ ] `src/api/http_routes.py` - 更新 STICKER_BASE_DIR
   - [ ] `src/core/config/settings.py` - 更新 database path
   - [ ] `src/utils/image_alter.py` - 更新 json path
   - [ ] `tools/sticker_manager/sticker_manager.py` - 更新多处路径

#### P2 - 中优先级（桌面应用）

7. **创建新文件：**
   - [ ] `src/desktop/__init__.py`
   - [ ] `src/desktop/main.py`
   - [ ] `src/desktop/window.py`
   - [ ] `src/desktop/config.py`
   - [ ] `src/core/utils/__init__.py`
   - [ ] `src/core/utils/paths.py`
   - [ ] `desktop.py`
   - [ ] `build/pyinstaller/desktop.spec`
   - [ ] `build/build_windows.bat`
   - [ ] `build/build_macos.sh`
   - [ ] `build/build_linux.sh`

8. **更新配置：**
   - [ ] `pyproject.toml` - 添加 pywebview, pyinstaller
   - [ ] `.gitignore` - 添加 build/, logs/
   - [ ] `README.md` - 添加桌面应用说明

---

## 🎯 最终目录结构 Final Directory Structure

```
Yuzuriha-Rin/
├── src/                              # 所有源代码
│   ├── frontend/                     # ★ 从根目录移入
│   │   ├── scripts/
│   │   ├── styles/
│   │   └── index.html
│   │
│   ├── api/                          # API 层
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   ├── schemas.py                # ★ 仅 API 专用 schemas
│   │   ├── http_routes.py            # ★ 重命名自 routes.py
│   │   ├── websocket_session.py      # ★ 重命名自 ws_routes.py
│   │   └── websocket_global.py       # ★ 重命名自 ws_global_routes.py
│   │
│   ├── core/                         # 核心领域
│   │   ├── __init__.py
│   │   ├── schemas.py                # ★ 新增：领域 schemas
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── models/                   # 领域模型
│   │   │   ├── __init__.py
│   │   │   ├── character.py
│   │   │   ├── message.py
│   │   │   ├── session.py
│   │   │   ├── behavior.py
│   │   │   └── constants.py
│   │   ├── interfaces/               # ★ 新增：抽象接口
│   │   │   ├── __init__.py
│   │   │   └── repositories.py
│   │   └── utils/                    # ★ 新增：核心工具
│   │       ├── __init__.py
│   │       ├── logger.py             # ★ 从 infrastructure 移入
│   │       └── paths.py              # ★ 新增：路径处理
│   │
│   ├── infrastructure/               # 基础设施层
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── base.py           # ★ 移到 core/interfaces/
│   │   │       ├── character_repo.py # ★ 实现接口
│   │   │       ├── message_repo.py   # ★ 实现接口
│   │   │       ├── session_repo.py   # ★ 实现接口
│   │   │       └── config_repo.py    # ★ 实现接口
│   │   └── network/
│   │       ├── __init__.py
│   │       ├── websocket_manager.py
│   │       └── port_manager.py
│   │
│   ├── services/                     # 应用服务层
│   │   ├── __init__.py
│   │   ├── behavior/
│   │   ├── character/
│   │   │   ├── __init__.py
│   │   │   └── character_service.py  # ★ 依赖抽象接口
│   │   ├── config/
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   └── llm_client.py         # ★ 更新 schemas 导入
│   │   ├── messaging/
│   │   │   ├── __init__.py
│   │   │   └── message_service.py    # ★ 依赖抽象接口
│   │   ├── session/
│   │   │   ├── __init__.py
│   │   │   └── session_client.py     # ★ 更新 schemas 导入
│   │   └── tools/
│   │
│   ├── desktop/                      # ★ 新增：桌面应用
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── window.py
│   │   └── config.py
│   │
│   └── utils/                        # 通用工具
│       ├── __init__.py
│       ├── image_alter.py            # ★ 更新 json 路径
│       └── url_utils.py
│
├── tests/                            # 测试
│
├── scripts/                          # ★ 重命名自 models/
│   └── ml_training/
│       ├── train_wechat_v2.py
│       ├── predict_windows.py
│       └── ...
│
├── tools/                            # 独立工具
│   └── sticker_manager/
│
├── data/                             # ★ 仅运行时数据
│   └── database/
│       └── rin_app.db
│
├── assets/                           # ★ 新增：应用资源
│   ├── stickers/                     # ★ 从 data/ 移入
│   ├── jieba/                        # ★ 从 data/ 移入
│   └── config/
│       └── image_descriptions.json   # ★ 重命名并移入
│
├── archive/                          # ★ 新增：归档资源
│   └── raw/                          # ★ 从 data/raw 移入
│
├── build/                            # ★ 新增：打包配置
│   ├── pyinstaller/
│   │   ├── desktop.spec
│   │   └── hooks/
│   ├── icons/
│   │   ├── app.ico
│   │   ├── app.icns
│   │   └── app.png
│   ├── build_windows.bat
│   ├── build_macos.sh
│   └── build_linux.sh
│
├── logs/                             # ★ 新增：日志文件
│
├── run.py                            # Web 服务入口
├── desktop.py                        # ★ 新增：桌面应用入口
├── pyproject.toml                    # ★ 更新依赖
├── .gitignore                        # ★ 更新
└── README.md                         # ★ 更新

★ = 需要修改或新增
```

---

## 🔄 依赖关系图（重构后）Dependency Graph After Refactoring

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│                    (src/api/, src/desktop/)             │
│                                                         │
│  依赖：Services, Schemas, Infrastructure（仅创建）     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│                      (src/services/)                    │
│                                                         │
│  依赖：Core (schemas, models, interfaces)               │
│  不依赖：Infrastructure（仅接口，不依赖实现）          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                       │
│      (src/core/models/, schemas, interfaces)            │
│                                                         │
│  依赖：无（完全独立）                                   │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │
┌────────────────────────┴────────────────────────────────┐
│                 Infrastructure Layer                    │
│            (src/infrastructure/)                        │
│                                                         │
│  依赖：Core (实现 interfaces)                           │
│  被依赖：仅通过接口                                     │
└─────────────────────────────────────────────────────────┘

依赖规则 Dependency Rules:
✅ Presentation → Application → Domain
✅ Infrastructure → Domain (implements interfaces)
✅ Presentation → Infrastructure (只用于创建实例)
❌ Application → Infrastructure (只能依赖接口)
❌ Domain → 任何层
```

---

## ⚠️ 风险评估 Risk Assessment

| 阶段 | 风险等级 | 影响范围 | 建议缓解措施 |
|------|---------|---------|-------------|
| **阶段 1：分层架构修复** | 🟡 中 | 核心服务层 | • 分步执行<br>• 每步后运行测试<br>• 先修复一个服务测试 |
| **阶段 2：目录重组** | 🟢 低 | 路径引用 | • 一次移动一个目录<br>• 立即更新引用<br>• 测试每次变更 |
| **阶段 3：桌面应用** | 🟢 低 | 新增功能 | • 独立开发<br>• 不影响现有功能 |
| **阶段 4：文档更新** | 🟢 极低 | 文档 | • 最后执行 |

---

## 📅 时间估算 Time Estimate

| 阶段 | 预计时间 | 说明 |
|------|---------|------|
| **阶段 1：分层架构修复** | 4-6 小时 | 核心重构，需要仔细处理 |
| **阶段 2：目录重组** | 1-2 小时 | 主要是移动和更新路径 |
| **阶段 3：桌面应用** | 3-4 小时 | 新功能开发 |
| **阶段 4：文档更新** | 1 小时 | 更新文档 |
| **测试和验证** | 2-3 小时 | 全面测试 |
| **总计** | **11-16 小时** | 分多天完成 |

---

## ✅ 完成标准 Definition of Done

### 阶段 1 完成标准：
- [ ] 所有服务层不再直接导入 `src.api.*`
- [ ] 所有服务层不再直接导入具体仓储实现
- [ ] 所有仓储实现了对应的接口
- [ ] 单元测试通过
- [ ] 集成测试通过

### 阶段 2 完成标准：
- [ ] frontend 在 `src/frontend/`
- [ ] ML 脚本在 `scripts/ml_training/`
- [ ] API 路由文件语义化命名
- [ ] assets/ 和 archive/ 正确组织
- [ ] 所有路径引用正确
- [ ] 应用正常启动和运行

### 阶段 3 完成标准：
- [ ] 桌面应用可以通过 `python desktop.py` 启动
- [ ] PyInstaller 可以成功打包
- [ ] 打包后的应用可以正常运行
- [ ] 所有资源正确打包

### 阶段 4 完成标准：
- [ ] 所有文档更新完成
- [ ] README 包含桌面应用说明
- [ ] 架构图更新

---

## 🚀 执行建议 Execution Recommendations

### 推荐执行顺序：

1. **先执行阶段 1（P0）：** 修复分层架构违规
   - 这是最重要的，影响代码质量和可维护性
   - 一旦修复，后续开发会更规范

2. **再执行阶段 2（P1）：** 目录和命名优化
   - 在架构正确后，优化组织更安全
   - 便于后续桌面应用开发

3. **最后执行阶段 3（P2）：** 桌面应用
   - 基于正确的架构开发新功能
   - 不影响现有 Web 应用

4. **持续执行阶段 4：** 文档更新
   - 每个阶段完成后更新对应文档

### 分支策略：

```bash
# 主分支
main

# 重构分支
refactor/layered-architecture    # 阶段 1
refactor/directory-organization  # 阶段 2
feature/desktop-app              # 阶段 3
```

---

## 📞 需要决策的问题 Decision Points

### 1. 日志依赖解决方案

**选项 A：** 创建接口 + 依赖注入（完全符合 DIP）
**选项 B：** 移动到 core/utils/（简单快速）

**推荐：方案 B**

### 2. schemas 放置位置

**选项 A：** `src/core/schemas.py`（单文件）
**选项 B：** `src/core/models/schemas.py`（在 models 下）
**选项 C：** 分散到各服务（如 `src/services/llm/schemas.py`）

**推荐：方案 A**

### 3. 路由命名方案

**方案 A：** `http_routes.py`, `websocket_session.py`, `websocket_global.py`
**方案 B：** 按业务领域分离（`character_routes.py` 等）

**推荐：方案 A**（当前项目规模适合）

---

## 📝 总结 Summary

本重构计划包含 **4 个阶段**，**80+ 个任务**，涉及：

1. **修复分层架构违规**（零容忍问题）
   - 引入仓储接口（依赖倒置）
   - 移动 schemas 到正确位置
   - 解决日志依赖问题

2. **优化目录和命名**
   - 移动 frontend 到 src/
   - 重命名 models/ 为 scripts/ml_training/
   - API 路由文件语义化
   - 重组 data/ 和创建 assets/

3. **准备桌面应用**
   - 创建 desktop 模块
   - 路径处理工具
   - PyInstaller 配置

4. **文档更新**
   - 更新所有架构文档
   - 添加桌面应用指南

**预计总时间：11-16 小时**

执行此计划后，项目将：
- ✅ 完全符合分层架构原则
- ✅ 遵循 SOLID 原则
- ✅ 易于测试和维护
- ✅ 支持桌面应用打包
- ✅ 目录组织清晰合理

---

**文档创建时间：** 2025-12-15  
**项目版本：** 0.1.0  
**作者：** GitHub Copilot Coding Agent
