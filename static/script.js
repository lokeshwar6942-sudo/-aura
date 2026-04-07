document.addEventListener('DOMContentLoaded', () => {
    const chatBody = document.getElementById('chat-body');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    
    // Generate a simple session ID to keep chat context active on the server
    const sessionId = Math.random().toString(36).substring(2, 15);

    function scrollToBottom() {
        chatBody.scrollTo({
            top: chatBody.scrollHeight,
            behavior: 'smooth'
        });
    }

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'assistant-message');

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        if (isUser) {
            contentDiv.textContent = content;
        } else {
            // marked.js converts AI's markdown response to HTML nicely
            contentDiv.innerHTML = marked.parse(content);
        }

        messageDiv.appendChild(contentDiv);
        chatBody.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.classList.add('message', 'assistant-message');
        indicatorDiv.id = 'typing-indicator-wrapper';
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('typing-indicator-container');
        
        const dotsDiv = document.createElement('div');
        dotsDiv.classList.add('typing-indicator');
        dotsDiv.innerHTML = '<span></span><span></span><span></span>';
        
        contentDiv.appendChild(dotsDiv);
        indicatorDiv.appendChild(contentDiv);
        chatBody.appendChild(indicatorDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator-wrapper');
        if (indicator) {
            indicator.remove();
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Disable input while processing to prevent spam
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        addMessage(message, true);
        addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message, session_id: sessionId })
            });

            removeTypingIndicator();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response error');
            }

            const data = await response.json();
            
            // Artificial small delay for a more natural feel
            setTimeout(() => {
                addMessage(data.reply, false);
            }, 300);

        } catch (error) {
            removeTypingIndicator();
            console.error('Error:', error);
            
            let errorMsg = "Sorry, I am currently offline or encountered a network error.";
            if (error.message.includes("API Key")) {
                errorMsg = "⚠️ Setup Required: Please add your Google Gemini API Key in the `.env` file and restart the server.";
            }
            
            addMessage(errorMsg, false);
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Auto focus the input field when the page loads
    userInput.focus();
});
