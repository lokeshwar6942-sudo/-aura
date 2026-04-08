document.addEventListener('DOMContentLoaded', () => {
    const chatBody = document.getElementById('chat-body');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const sessionId = Math.random().toString(36).substring(2, 15);

    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = isUser ? content : marked.parse(content);

        messageDiv.appendChild(contentDiv);
        chatBody.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
        chatBody.appendChild(typingDiv);
        scrollToBottom();
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = '';
        addMessage(text, true);
        addTyping();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            
            document.getElementById('typing-indicator')?.remove();
            const data = await res.json();
            addMessage(data.reply, false);
        } catch (err) {
            document.getElementById('typing-indicator')?.remove();
            addMessage("⚠️ Connection Error. Please try again.", false);
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });
});
