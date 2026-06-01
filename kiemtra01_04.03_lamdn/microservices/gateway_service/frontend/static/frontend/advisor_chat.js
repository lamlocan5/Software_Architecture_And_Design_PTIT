/**
 * AI Advisor Chat Widget — advisor_chat.js
 * Floating chat button + RAG chatbot integration
 */

(function () {
    'use strict';

    const ADVISOR_URL = '/api/advisor/chat/';
    const TRACK_URL   = '/api/advisor/track/';

    const WELCOME_SUGGESTIONS = [
        '💻 Laptop cho sinh viên giá 15 triệu',
        '📱 Điện thoại chụp ảnh đẹp',
        '🎮 Laptop gaming mạnh nhất',
        '⚡ So sánh iPhone vs Samsung',
    ];

    let sessionId = null;
    let isOpen    = false;
    let isLoading = false;

    /* ────────────────────────────────────────────────────────────
       Khởi tạo widget
    ──────────────────────────────────────────────────────────── */
    function init() {
        injectHTML();
        bindEvents();
        setTimeout(() => {
            const fab = document.getElementById('advisor-fab');
            if (fab) {
                fab.classList.add('fab-has-notification');
                setTimeout(() => fab.classList.remove('fab-has-notification'), 5000);
            }
        }, 3000);
    }

    /* ────────────────────────────────────────────────────────────
       Inject HTML vào DOM
    ──────────────────────────────────────────────────────────── */
    function injectHTML() {
        const fabHtml = `
        <button id="advisor-fab" title="Tư vấn AI" aria-label="Mở chat tư vấn AI">
            🤖
            <span class="fab-tooltip">Tư vấn AI miễn phí!</span>
            <span class="fab-badge">1</span>
        </button>`;

        const panelHtml = `
        <div id="advisor-chat-panel" role="dialog" aria-label="Chat tư vấn AI" aria-hidden="true">
            <!-- Header -->
            <div class="chat-header">
                <div class="chat-avatar">🤖</div>
                <div class="chat-header-info">
                    <div class="chat-header-title">AI Tư Vấn TechStore</div>
                    <div class="chat-header-status">Đang hoạt động</div>
                </div>
                <div class="chat-header-actions">
                    <button class="chat-header-btn" id="chatClearBtn" title="Xóa lịch sử" aria-label="Xóa lịch sử chat">🗑</button>
                    <button class="chat-header-btn" id="chatCloseBtn" title="Đóng" aria-label="Đóng chat">✕</button>
                </div>
            </div>

            <!-- Messages -->
            <div class="chat-messages" id="chatMessages" role="log" aria-live="polite">
                <div class="chat-welcome">
                    <div class="chat-welcome-icon">🛍️</div>
                    <div class="chat-welcome-title">Chào mừng đến TechStore!</div>
                    <div class="chat-welcome-desc">Tôi là trợ lý AI, sẵn sàng tư vấn laptop và điện thoại phù hợp với nhu cầu của bạn.</div>
                </div>
            </div>

            <!-- Typing indicator -->
            <div class="chat-msg bot-msg chat-typing" id="chatTyping">
                <div class="msg-icon bot-icon">🤖</div>
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>

            <!-- Suggestions -->
            <div class="chat-suggestions" id="chatSuggestions">
                ${WELCOME_SUGGESTIONS.map(s =>
                    `<button class="suggestion-chip" onclick="advisorSendSuggestion('${s.replace(/'/g, "\\'")}')">
                        ${s}
                    </button>`
                ).join('')}
            </div>

            <!-- Input -->
            <div class="chat-input-area">
                <textarea
                    id="advisorInput"
                    placeholder="Nhập câu hỏi tư vấn..."
                    rows="1"
                    aria-label="Nhập câu hỏi"
                ></textarea>
                <button id="advisorSendBtn" title="Gửi" aria-label="Gửi tin nhắn">➤</button>
            </div>
        </div>`;

        document.body.insertAdjacentHTML('beforeend', fabHtml + panelHtml);
    }

    /* ────────────────────────────────────────────────────────────
       Bind events
    ──────────────────────────────────────────────────────────── */
    function bindEvents() {
        document.getElementById('advisor-fab').addEventListener('click', toggleChat);
        document.getElementById('chatCloseBtn').addEventListener('click', closeChat);
        document.getElementById('chatClearBtn').addEventListener('click', clearChat);

        const input = document.getElementById('advisorInput');
        const sendBtn = document.getElementById('advisorSendBtn');

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        input.addEventListener('input', () => {
            // Auto-resize textarea
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        });

        sendBtn.addEventListener('click', sendMessage);

        // Đóng khi click bên ngoài
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('advisor-chat-panel');
            const fab   = document.getElementById('advisor-fab');
            if (isOpen && !panel.contains(e.target) && !fab.contains(e.target)) {
                closeChat();
            }
        });
    }

    /* ────────────────────────────────────────────────────────────
       Toggle open/close
    ──────────────────────────────────────────────────────────── */
    function toggleChat() {
        isOpen ? closeChat() : openChat();
    }

    function openChat() {
        isOpen = true;
        const panel = document.getElementById('advisor-chat-panel');
        const fab   = document.getElementById('advisor-fab');
        panel.classList.add('chat-open');
        panel.setAttribute('aria-hidden', 'false');
        fab.style.animation = 'none';
        fab.classList.remove('fab-has-notification');
        setTimeout(() => document.getElementById('advisorInput').focus(), 300);
        scrollToBottom();
    }

    function closeChat() {
        isOpen = false;
        const panel = document.getElementById('advisor-chat-panel');
        panel.classList.remove('chat-open');
        panel.setAttribute('aria-hidden', 'true');
        document.getElementById('advisor-fab').style.animation = '';
    }

    /* ────────────────────────────────────────────────────────────
       Send message
    ──────────────────────────────────────────────────────────── */
    function sendMessage() {
        const input = document.getElementById('advisorInput');
        const text  = input.value.trim();
        if (!text || isLoading) return;

        // Ẩn suggestions sau lần chat đầu
        hideSuggestions();

        appendMessage('user', text);
        input.value = '';
        input.style.height = 'auto';

        showTyping();
        setLoading(true);

        const customerId = getCustomerId();

        fetch(ADVISOR_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query:       text,
                customer_id: customerId,
                session_id:  getCurrentSession(),
            }),
        })
        .then(r => r.json())
        .then(data => {
            hideTyping();
            setLoading(false);
            if (data.session_id) sessionId = data.session_id;
            const reply = data.response || 'Xin lỗi, hệ thống tạm thời không phản hồi. Vui lòng thử lại.';
            appendMessage('bot', reply);
        })
        .catch(() => {
            hideTyping();
            setLoading(false);
            appendMessage('bot', '⚠️ Không thể kết nối tới AI Advisor. Vui lòng kiểm tra kết nối và thử lại.');
        });
    }

    /* ────────────────────────────────────────────────────────────
       DOM helpers
    ──────────────────────────────────────────────────────────── */
    function appendMessage(role, text) {
        const messages = document.getElementById('chatMessages');
        const isUser   = role === 'user';
        const now      = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

        const div = document.createElement('div');
        div.className = `chat-msg ${isUser ? 'user-msg' : 'bot-msg'}`;
        div.innerHTML = `
            <div class="msg-icon ${isUser ? 'user-icon' : 'bot-icon'}">${isUser ? '👤' : '🤖'}</div>
            <div>
                <div class="msg-bubble">${formatMessage(text)}</div>
                <div class="msg-time">${now}</div>
            </div>`;

        messages.appendChild(div);
        scrollToBottom();
    }

    function formatMessage(text) {
        // Basic markdown-like formatting
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.+?)`/g, '<code style="background:rgba(255,255,255,0.1);padding:1px 4px;border-radius:3px;font-size:0.85em">$1</code>')
            .replace(/\n/g, '<br>');
    }

    function showTyping() {
        const typing = document.getElementById('chatTyping');
        typing.classList.add('visible');
        scrollToBottom();
    }

    function hideTyping() {
        document.getElementById('chatTyping').classList.remove('visible');
    }

    function hideSuggestions() {
        const sug = document.getElementById('chatSuggestions');
        if (sug) {
            sug.style.transition = 'opacity 0.2s';
            sug.style.opacity = '0';
            setTimeout(() => (sug.style.display = 'none'), 200);
        }
    }

    function scrollToBottom() {
        const messages = document.getElementById('chatMessages');
        if (messages) {
            setTimeout(() => (messages.scrollTop = messages.scrollHeight), 50);
        }
    }

    function setLoading(state) {
        isLoading = state;
        const btn = document.getElementById('advisorSendBtn');
        if (btn) btn.disabled = state;
    }

    function clearChat() {
        const messages = document.getElementById('chatMessages');
        messages.innerHTML = `
            <div class="chat-welcome">
                <div class="chat-welcome-icon">🛍️</div>
                <div class="chat-welcome-title">Đã xóa lịch sử!</div>
                <div class="chat-welcome-desc">Bắt đầu cuộc trò chuyện mới với AI Tư Vấn.</div>
            </div>`;
        sessionId = null;

        // Restore suggestions
        const sug = document.getElementById('chatSuggestions');
        if (sug) {
            sug.style.display = '';
            sug.style.opacity = '1';
        }
    }

    /* ────────────────────────────────────────────────────────────
       Utility
    ──────────────────────────────────────────────────────────── */
    function getCustomerId() {
        const token = localStorage.getItem('token');
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.user_id || payload.id || null;
        } catch {
            return null;
        }
    }

    function getCurrentSession() {
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).slice(2) + '_' + Date.now();
        }
        return sessionId;
    }

    /* ────────────────────────────────────────────────────────────
       Behaviour Tracking — gửi event khi user xem sản phẩm
    ──────────────────────────────────────────────────────────── */
    window.advisorTrack = function (eventData) {
        const customerId = getCustomerId();
        if (!customerId) return;
        fetch(TRACK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...eventData, customer_id: customerId }),
        }).catch(() => { /* silent fail */ });
    };

    /* ────────────────────────────────────────────────────────────
       Public API
    ──────────────────────────────────────────────────────────── */
    window.advisorSendSuggestion = function (text) {
        const input = document.getElementById('advisorInput');
        if (input) {
            input.value = text;
            sendMessage();
        }
    };

    window.openAdvisorChat = openChat;
    window.closeAdvisorChat = closeChat;

    /* ────────────────────────────────────────────────────────────
       Khởi chạy sau khi DOM ready
    ──────────────────────────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
