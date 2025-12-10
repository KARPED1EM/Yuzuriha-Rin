class ChatApp {
    constructor() {
        this.config = null;
        this.sessionId = this.loadOrCreateSessionId();
        this.ws = null;
        this.isProcessing = false;
        this.messageRefs = new Map();

        this.initElements();
        this.attachEventListeners();
        this.loadSavedConfig();
    }

    loadOrCreateSessionId() {
        const existing = localStorage.getItem('conversationId');
        if (existing) return existing;

        const uuid = this.createSessionId();
        localStorage.setItem('conversationId', uuid);
        return uuid;
    }

    createSessionId() {
        const fallback = `conv-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
        return (window.crypto && window.crypto.randomUUID)
            ? window.crypto.randomUUID()
            : fallback;
    }

    initElements() {
        this.configPanel = document.getElementById('configPanel');
        this.providerSelect = document.getElementById('provider');
        this.apiKeyInput = document.getElementById('apiKey');
        this.baseUrlInput = document.getElementById('baseUrl');
        this.baseUrlGroup = document.getElementById('baseUrlGroup');
        this.modelInput = document.getElementById('model');
        this.personaInput = document.getElementById('personaInput');
        this.characterNameInput = document.getElementById('characterName');
        this.emotionThemeToggle = document.getElementById('emotionThemeToggle');
        this.saveConfigBtn = document.getElementById('saveConfig');

        this.chatContainer = document.getElementById('chatContainer');
        this.wechatShell = document.querySelector('.wechat-shell');
        this.chatTitle = document.getElementById('chatTitle');
        this.messagesDiv = document.getElementById('messages');
        this.userInput = document.getElementById('userInput');
        this.toggleBtn = document.getElementById('toggleBtn');
        this.showConfigBtn = document.getElementById('showConfig');
        this.statusTime = document.getElementById('statusTime');
        this.plusBtn = document.querySelector('.plus-btn');

        this.defaultTitle = this.chatTitle.textContent || 'Rin';

        if (this.statusTime) {
            this.statusTime.textContent = this.getCurrentTime();
        }
    }

    attachEventListeners() {
        this.providerSelect.addEventListener('change', () => {
            const isCustom = this.providerSelect.value === 'custom';
            this.baseUrlGroup.style.display = isCustom ? 'block' : 'none';

            const defaults = {
                'deepseek': 'deepseek-chat',
                'openai': 'gpt-3.5-turbo',
                'anthropic': 'claude-3-5-sonnet-20241022',
                'custom': 'gpt-3.5-turbo'
            };
            this.modelInput.value = defaults[this.providerSelect.value];
        });

        this.saveConfigBtn.addEventListener('click', () => this.saveConfig());
        this.showConfigBtn.addEventListener('click', () => this.toggleView());

        this.toggleBtn.addEventListener('click', () => {
            if (!this.toggleBtn.disabled) {
                this.sendMessage();
            }
        });

        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !this.isProcessing) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.userInput.addEventListener('input', () => this.updateComposerState());

        if (this.emotionThemeToggle) {
            this.emotionThemeToggle.addEventListener('change', () => {
                if (!this.emotionThemeToggle.checked) {
                    this.clearEmotionTheme();
                }
            });
        }
    }

    loadSavedConfig() {
        const saved = localStorage.getItem('chatConfig');
        if (saved) {
            try {
                const config = JSON.parse(saved);
                this.providerSelect.value = config.provider || 'openai';
                this.apiKeyInput.value = config.api_key || '';
                this.baseUrlInput.value = config.base_url || '';
                this.modelInput.value = config.model || 'gpt-3.5-turbo';
                this.personaInput.value = config.persona || '';
                this.characterNameInput.value = config.character_name || 'Rin';
                if (this.emotionThemeToggle) {
                    this.emotionThemeToggle.checked = config.enable_emotion_theme !== false;
                }

                this.providerSelect.dispatchEvent(new Event('change'));
            } catch (e) {
                console.error('Failed to load config:', e);
            }
        }
    }

    saveConfig() {
        const apiKey = this.apiKeyInput.value.trim();
        if (!apiKey) {
            alert('Please enter API key');
            return;
        }

        this.config = {
            provider: this.providerSelect.value,
            api_key: apiKey,
            base_url: this.baseUrlInput.value.trim() || null,
            model: this.modelInput.value.trim(),
            persona: this.personaInput.value.trim(),
            character_name: this.characterNameInput.value.trim() || 'Rin',
            enable_emotion_theme: this.emotionThemeToggle ? this.emotionThemeToggle.checked : false
        };

        this.sessionId = this.createSessionId();
        localStorage.setItem('conversationId', this.sessionId);

        localStorage.setItem('chatConfig', JSON.stringify(this.config));
        this.toggleView();
        this.enableChat();
        this.connectWebSocket();
    }

    toggleView() {
        const showChat = this.configPanel.style.display !== 'none';
        this.configPanel.style.display = showChat ? 'none' : 'block';
        this.chatContainer.style.display = showChat ? 'flex' : 'none';

        if (showChat && this.config) {
            this.defaultTitle = this.config.character_name || 'Rin';
            this.chatTitle.textContent = this.defaultTitle;
        }
    }

    enableChat() {
        this.userInput.disabled = false;
        this.toggleBtn.disabled = true;
        this.userInput.focus();
        this.updateComposerState();
    }

    connectWebSocket() {
        if (this.ws) {
            this.ws.close();
        }

        // For local development, always use localhost instead of 0.0.0.0
        let host = window.location.host;
        if (host.startsWith('0.0.0.0:')) {
            host = host.replace('0.0.0.0:', 'localhost:');
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${host}/api/ws/${this.sessionId}?user_id=user`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.sendInitRin();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage('system', 'Connection error. Please refresh the page.');
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed');
        };
    }

    sendInitRin() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        this.ws.send(JSON.stringify({
            type: 'init_rin',
            llm_config: this.config
        }));
    }

    handleWebSocketMessage(data) {
        const type = data.type;

        if (type === 'history') {
            this.handleHistory(data.data);
        } else if (type === 'message') {
            this.handleMessage(data.data);
        } else if (type === 'typing') {
            this.handleTyping(data.data);
        } else if (type === 'recall') {
            this.handleRecall(data.data);
        } else if (type === 'clear') {
            this.handleClear(data.data);
        }
    }

    handleHistory(data) {
        this.messagesDiv.innerHTML = '';
        this.messageRefs.clear();

        const messages = data.messages || [];
        for (const msg of messages) {
            if (msg.type === 'text') {
                const role = msg.sender_id === 'user' ? 'user' : 'assistant';
                const messageDiv = this.addMessage(role, msg.content, {
                    messageId: msg.id,
                    emotion: msg.metadata?.emotion
                });
                this.messageRefs.set(msg.id, messageDiv);
            } else if (msg.type === 'recalled') {
                this.showRecallNotice();
            }
        }
    }

    handleMessage(data) {
        const role = data.sender_id === 'user' ? 'user' : 'assistant';
        const messageDiv = this.addMessage(role, data.content, {
            messageId: data.id,
            emotion: data.metadata?.emotion
        });

        if (data.id) {
            this.messageRefs.set(data.id, messageDiv);
        }

        if (role === 'assistant' && this.emotionThemeToggle?.checked) {
            this.applyEmotionFromMetadata(data.metadata);
        }
    }

    handleTyping(data) {
        if (data.user_id === 'rin') {
            this.setTypingStatus(data.is_typing);
        }
    }

    handleRecall(data) {
        const messageId = data.message_id;
        if (messageId && this.messageRefs.has(messageId)) {
            const messageDiv = this.messageRefs.get(messageId);
            if (messageDiv) {
                messageDiv.remove();
            }
            this.messageRefs.delete(messageId);
            this.showRecallNotice();
        }
    }

    handleClear(data) {
        this.messagesDiv.innerHTML = '';
        this.messageRefs.clear();
    }

    addMessage(role, content, options = {}) {
        const row = document.createElement('div');
        row.className = `message-row ${role}`;

        if (role === 'system') {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = content;
            row.appendChild(bubble);
        } else {
            const avatar = document.createElement('img');
            avatar.className = 'avatar';
            avatar.src = role === 'user'
                ? '/static/assets/avatar_user.png'
                : '/static/assets/avatar_rin.png';
            avatar.alt = role === 'user' ? 'Me' : 'Rin';

            const bubble = document.createElement('div');
            bubble.className = `bubble ${role}`;
            bubble.textContent = content;

            if (options.emotion) {
                bubble.dataset.emotion = options.emotion;
            }

            row.appendChild(avatar);
            row.appendChild(bubble);
        }

        if (options.messageId) {
            row.dataset.messageId = options.messageId;
        }

        this.messagesDiv.appendChild(row);
        this.scrollToBottom();
        return row;
    }

    scrollToBottom() {
        this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
    }

    sendMessage() {
        const text = this.userInput.value.trim();
        if (!text || this.isProcessing || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        this.isProcessing = true;
        this.userInput.value = '';
        this.updateComposerState();

        const messageId = `msg-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;

        this.ws.send(JSON.stringify({
            type: 'message',
            id: messageId,
            content: text,
            metadata: {}
        }));

        this.isProcessing = false;
        this.userInput.focus();
    }

    clearConversation() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        this.ws.send(JSON.stringify({
            type: 'clear'
        }));
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    updateComposerState() {
        const hasText = this.userInput.value.trim().length > 0;
        if (hasText) {
            this.plusBtn.classList.add('hidden');
            this.toggleBtn.classList.remove('hidden');
            this.toggleBtn.disabled = false;
        } else {
            this.plusBtn.classList.remove('hidden');
            this.toggleBtn.classList.add('hidden');
            this.toggleBtn.disabled = true;
        }
    }

    setTypingStatus(active) {
        if (!this.chatTitle) return;
        this.chatTitle.textContent = active ? "对方正在输入中..." : (this.defaultTitle || 'Rin');
    }

    showRecallNotice() {
        const name = this.config?.character_name || 'Rin';
        const text = `"${name}" 撤回了一条消息`;
        this.addMessage('system', text);
    }

    applyEmotionFromMetadata(metadata) {
        if (!metadata || !this.emotionThemeToggle?.checked) {
            this.clearEmotionTheme();
            return;
        }

        const emotionMap = metadata.emotion_map || metadata.emotionMap;
        if (!emotionMap) {
            this.clearEmotionTheme();
            return;
        }

        this.wechatShell.classList.add('glow-enabled');
    }

    clearEmotionTheme() {
        if (!this.wechatShell) return;
        this.wechatShell.classList.remove('glow-enabled');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
