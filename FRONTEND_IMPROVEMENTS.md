# 前端本地持久化和增量同步改进

## 🎯 改进目标

实现类似微信的体验：
1. 消息本地持久化，刷新不丢失
2. 增量同步，只拉取本地没有的消息
3. 离线体验，用户离开再回来能看到完整历史
4. Rin发消息过程中刷新，回来后能看到已发送的部分

## ✅ 实现的功能

### 1. 本地消息持久化 (localStorage)

每个会话的消息存储在独立的localStorage key中：
```javascript
// 存储格式
localStorage.setItem(`messages_${conversationId}`, JSON.stringify(messages))
```

**存储内容**：
- 消息ID
- 会话ID
- 发送者ID
- 消息类型（text/recalled/system）
- 消息内容
- 时间戳
- 元数据（情绪等）

### 2. 增量同步机制

**原理**：
- 记录本地最后一条消息的时间戳
- 连接WebSocket时请求增量数据
- 只拉取比本地更新的消息

**实现流程**：
```
1. 页面加载 → 从localStorage加载本地消息
2. 渲染本地消息到界面
3. 连接WebSocket
4. 发送sync请求，携带lastTimestamp
5. 服务器返回新消息
6. 合并到本地并更新界面
```

### 3. 页面可见性监听

监听页面切换，实现：
```javascript
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // 用户离开：保存本地消息
        this.saveLocalMessages();
    } else {
        // 用户回来：同步新消息
        this.syncMessages();
    }
});
```

### 4. 自动重连机制

WebSocket断开后自动重连：
```javascript
ws.onclose = () => {
    setTimeout(() => {
        this.connectWebSocket(); // 3秒后重连
    }, 3000);
};
```

## 🔄 消息同步流程

### 首次打开
```
1. 加载localStorage中的本地消息
2. 渲染到界面
3. 连接WebSocket
4. 发送sync请求(after_timestamp=本地最新时间戳)
5. 接收服务器增量消息
6. 合并并更新界面
```

### 用户发送消息
```
1. 立即保存到localStorage
2. 立即渲染到界面
3. 通过WebSocket发送到服务器
4. 服务器广播给所有客户端(包括自己)
5. 收到广播后，去重(已存在则跳过)
```

### Rin发消息过程中用户离开
```
场景: Rin正在发送5条消息，用户在第2条后刷新

流程:
1. 用户打开页面
2. 加载本地消息(用户的消息 + Rin的前2条)
3. 渲染到界面
4. 连接WebSocket
5. 发送sync请求(after_timestamp=第2条消息时间戳)
6. 服务器返回第3-5条消息
7. 合并并显示

结果: 用户看到完整的5条消息，无缝体验
```

### Rin发消息过程中用户回来
```
场景: Rin正在发送消息，用户在另一个标签页回来

流程:
1. visibilitychange触发
2. 自动调用syncMessages()
3. 拉取最新消息
4. 实时显示Rin正在发送的消息

结果: 用户看到最新状态 + 实时接收新消息
```

## 📊 数据流

### 消息发送流
```
用户输入
   ↓
本地存储 (立即)
   ↓
UI渲染 (立即)
   ↓
WebSocket发送
   ↓
服务器保存
   ↓
广播给所有客户端
   ↓
其他客户端接收
```

### 消息同步流
```
页面加载
   ↓
读取localStorage
   ↓
渲染本地消息
   ↓
连接WebSocket
   ↓
sync请求(after_timestamp)
   ↓
服务器查询新消息
   ↓
返回增量数据
   ↓
合并本地消息
   ↓
更新UI
```

## 🎨 核心改进点

### 1. 消息去重
```javascript
handleMessage(data) {
    // 检查是否已存在
    if (this.localMessages.has(data.id)) {
        return; // 跳过重复消息
    }

    // 新消息：保存并显示
    this.localMessages.set(data.id, data);
    this.saveLocalMessages();
    this.addMessageToUI(data);
}
```

### 2. 时间戳管理
```javascript
getLastSyncTimestamp() {
    let maxTimestamp = 0;
    for (const msg of this.localMessages.values()) {
        if (msg.timestamp > maxTimestamp) {
            maxTimestamp = msg.timestamp;
        }
    }
    return maxTimestamp;
}
```

### 3. 消息撤回
```javascript
handleRecall(data) {
    // 更新本地状态
    const msg = this.localMessages.get(messageId);
    msg.type = 'recalled';
    msg.content = '';

    // 更新UI
    messageDiv.remove();
    this.showRecallNotice();

    // 持久化
    this.saveLocalMessages();
}
```

### 4. 清空对话
```javascript
handleClear() {
    // 清空内存
    this.localMessages.clear();
    this.messageRefs.clear();

    // 清空UI
    this.messagesDiv.innerHTML = '';

    // 清空localStorage
    this.lastSyncTimestamp = 0;
    this.saveLocalMessages();
}
```

## 🔧 后端支持

### sync端点
```python
async def handle_sync(websocket, conversation_id, data):
    after_timestamp = data.get("after_timestamp", 0)

    # 查询增量消息
    messages = await message_service.get_messages(
        conversation_id,
        after_timestamp=after_timestamp
    )

    # 返回历史事件
    event = message_service.create_history_event(messages)
    await ws_manager.send_to_websocket(websocket, event.model_dump())
```

### 数据库查询优化
```python
def get_messages(conversation_id, after_timestamp=None):
    query = "SELECT * FROM messages WHERE conversation_id = ?"
    params = [conversation_id]

    if after_timestamp is not None:
        query += " AND timestamp > ?"
        params.append(after_timestamp)

    query += " ORDER BY timestamp ASC"

    return execute_query(query, params)
```

## 📱 类似微信的特性

### ✅ 已实现
- [x] 消息本地持久化
- [x] 刷新不丢失消息
- [x] 增量同步，节省流量
- [x] 离线查看历史消息
- [x] 自动重连
- [x] 消息去重
- [x] 撤回消息本地更新

### 🚀 可扩展
- [ ] 消息分页加载（向上滚动加载更多）
- [ ] 消息已读状态
- [ ] 离线消息队列
- [ ] 消息搜索
- [ ] 本地缓存大小限制
- [ ] 消息过期自动清理

## 🎯 性能优化

### 减少网络请求
- 首次加载：渲染本地消息（无网络请求）
- 增量同步：只请求新消息
- WebSocket：双向通信，无轮询

### 减少DOM操作
- 消息去重：避免重复渲染
- 批量渲染：首次加载批量渲染本地消息

### 内存管理
- 使用Map存储消息（快速查找）
- 及时清理已删除消息的DOM引用

## 📝 使用示例

### 用户场景1：正常聊天
```
1. 用户打开页面
2. 看到历史消息（localStorage）
3. 发送消息
4. Rin回复
5. 所有消息自动保存
```

### 用户场景2：刷新页面
```
1. 用户聊天中刷新页面
2. 立即看到之前的消息（localStorage）
3. WebSocket连接后同步新消息
4. 无缝继续聊天
```

### 用户场景3：Rin发消息中离开
```
1. Rin正在发送5条消息
2. 用户在第2条后关闭页面
3. 10分钟后用户回来
4. 看到完整的5条消息
5. 感觉Rin一直在等他
```

### 用户场景4：多设备同步
```
注意：当前实现是单设备单会话
多设备需要额外的账号系统和同步机制
```

## 🔍 调试技巧

### 查看本地消息
```javascript
// 控制台
JSON.parse(localStorage.getItem('messages_conv-xxx'))
```

### 清空本地消息
```javascript
// 控制台
localStorage.clear()
```

### 查看同步时间戳
```javascript
// 在app实例中
console.log(app.lastSyncTimestamp)
```

## 📚 技术细节

### localStorage容量
- 单域名限制：5-10MB
- 每条消息约0.5-2KB
- 可存储约5000-10000条消息

### 时间戳精度
- JavaScript：毫秒级
- 后端：秒级（转换）
- 同步时使用秒级比较

### 消息顺序
- 按timestamp排序
- 保证消息顺序正确
- 即使乱序接收也能正确显示

---

**改进日期**: 2025-12-09
**核心价值**: 真正实现类似微信的本地持久化和增量同步
**用户体验**: 刷新无感，离线查看，实时同步
