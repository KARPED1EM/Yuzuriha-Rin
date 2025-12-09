# 🚀 Quick Start Guide

## 最快上手方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python run.py
```

### 3. 打开浏览器

访问: `http://localhost:8000`

### 4. 配置LLM

在配置面板中:
- 选择Provider (OpenAI/Anthropic/Custom)
- 输入API Key
- 选择模型 (如 `gpt-3.5-turbo`)
- (可选) 修改系统提示词

### 5. 开始聊天

点击 "Save & Start Chat"，然后开始对话！

## 📋 完整功能列表

### ✅ 已实现

- **多LLM支持**: OpenAI、Anthropic、自定义API
- **智能分段**: 自动将长消息分段发送
- **情感检测**: 识别7种情绪状态
- **错别字模拟**: 基于情绪的自然错别字
- **撤回重发**: 模拟发现错误后的撤回行为
- **打字动画**: 逐字符显示效果
- **停顿预测**: 自然的消息间停顿
- **配置持久化**: 浏览器本地存储

### 🔄 预留接入点

- **BiLSTM-CRF分段模型**: 接口已实现，训练后即可接入
- **高级情感分析**: 可替换为BERT等模型
- **对话历史分析**: 可基于上下文调整行为

## 📁 项目结构

```
Rie_Kugimiya/
├── src/
│   ├── api/              # FastAPI后端
│   │   ├── main.py       # ✅ 应用入口
│   │   ├── routes.py     # ✅ API路由 + 行为集成
│   │   ├── schemas.py    # ✅ 数据模型
│   │   └── llm_client.py # ✅ LLM客户端
│   ├── behavior/         # ✅ 行为系统 (核心)
│   │   ├── coordinator.py # 行为协调器
│   │   ├── segmenter.py  # 分段器 (规则+ML接口)
│   │   ├── emotion.py    # 情感检测
│   │   ├── typo.py       # 错别字注入
│   │   ├── pause.py      # 停顿预测
│   │   └── models.py     # 数据模型
│   └── utils/
│       └── config.py     # ✅ 配置管理
├── frontend/             # ✅ Web界面
│   ├── index.html        # UI结构
│   ├── chat.js           # 聊天逻辑 + 动画
│   └── styles.css        # 现代化样式
├── tests/                # ✅ 测试套件
│   └── test_behavior.py  # 单元测试
├── run.py                # ✅ 快速启动脚本
├── requirements.txt      # ✅ 依赖列表
└── [文档]               # ✅ 完整文档
```

## 🎯 使用场景

### 基础对话

```python
# 发送消息后，你会看到:
# 1. 打字指示器出现
# 2. 消息分段显示 (如果消息较长)
# 3. 每段之间有自然停顿
# 4. 可能出现错别字和撤回
```

### 自定义行为

在前端localStorage中修改配置，或通过API请求传入:

```javascript
{
  "behavior_settings": {
    "enable_segmentation": true,
    "enable_typo": true,
    "enable_recall": true,
    "base_typo_rate": 0.08,    // 8%概率错别字
    "typo_recall_rate": 0.4    // 40%概率撤回
  }
}
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_behavior.py::TestSegmenter -v
```

## 📚 文档

- **README.md**: 项目概览
- **SETUP.md**: 详细安装指南
- **IMPLEMENTATION.md**: 技术实现细节
- **API_EXAMPLES.md**: API使用示例
- **PROJECT_SUMMARY.md**: 完整项目总结
- **QUICKSTART.md**: 本文档

## 🔧 常见问题

### Q: 如何更改API密钥?

A: 点击右上角的⚙️按钮，重新配置并保存

### Q: 如何禁用错别字?

A: 目前需要通过API请求传入 `behavior_settings`，前端UI待扩展

### Q: 如何接入自己的ML模型?

A: 参考 `IMPLEMENTATION.md` 中的 "ML Model Integration" 部分

### Q: 支持哪些LLM?

A: OpenAI (GPT系列)、Anthropic (Claude)、任何OpenAI兼容的API

### Q: 如何调整打字速度?

A: 修改 `src/behavior/pause.py` 中的 `predict_typing_speed` 方法

## 🎨 自定义

### 修改角色设定

在配置页面修改 "System Prompt":

```
You are Rie Kugimiya, a famous Japanese voice actress.
You are cute, energetic, and a bit sassy.
You love to tease but care deeply about others.
```

### 调整行为参数

编辑 `src/behavior/models.py` 中的 `BehaviorConfig`:

```python
class BehaviorConfig(BaseModel):
    base_typo_rate: float = 0.08  # 修改这里
    typo_recall_rate: float = 0.4  # 和这里
    # ... 更多配置
```

### 添加新情绪

1. 在 `src/behavior/models.py` 添加情绪类型
2. 在 `src/behavior/emotion.py` 添加关键词
3. 在 `frontend/styles.css` 添加对应样式

## 🚀 下一步

### 立即体验

```bash
python run.py
# 访问 http://localhost:8000
```

### 训练ML模型

参考 `IMPLEMENTATION.md` 中的模型训练步骤

### 贡献代码

欢迎提交PR改进系统！

## 💡 技术亮点

1. **模块化架构**: 每个组件独立可测
2. **ML就绪**: 预留完整的模型接入接口
3. **类型安全**: 全程使用Pydantic验证
4. **异步优先**: FastAPI + HTTPX
5. **优雅降级**: ML模型不可用时自动使用规则
6. **实时动画**: 流畅的打字和过渡效果

## 📞 支持

遇到问题? 查看:
- Issues on GitHub
- IMPLEMENTATION.md
- API_EXAMPLES.md

---

**开始使用**: `python run.py`

**项目状态**: ✅ 生产就绪 (除ML模型外)

**核心价值**: 完整的行为模拟系统 + ML接入架构
