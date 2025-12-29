let isLoading = false;

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    if (isLoading) return;
    
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    const useMCP = document.getElementById('useMCP').checked;
    
    // Clear input
    userInput.value = '';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Update status
    setStatus('loading', 'Thinking...');
    isLoading = true;
    document.getElementById('sendBtn').disabled = true;
    
    try {
        const response = await fetch('/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                use_mcp: useMCP
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Add assistant response to chat
        addMessage(data.response, 'assistant');
        
        // Update model info
        document.getElementById('modelInfo').textContent = `Model: ${data.model}`;
        
        setStatus('ready', 'Ready');
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your request.', 'assistant', true);
        setStatus('ready', 'Error occurred');
    } finally {
        isLoading = false;
        document.getElementById('sendBtn').disabled = false;
        userInput.focus();
    }
}

function addMessage(content, role, isError = false) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Remove welcome message if it exists
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    if (isError) {
        contentDiv.style.color = '#d32f2f';
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function setStatus(state, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    indicator.className = state;
    statusText.textContent = text;
}

async function clearChat() {
    if (!confirm('Are you sure you want to clear the chat history?')) {
        return;
    }
    
    try {
        await fetch('/api/clear', {
            method: 'POST'
        });
        
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>Welcome! 👋</h2>
                <p>Ask me anything. I'm powered by Groq with HuggingFace fallback.</p>
            </div>
        `;
        
        document.getElementById('modelInfo').textContent = '';
        
    } catch (error) {
        console.error('Error clearing chat:', error);
        alert('Failed to clear chat history');
    }
}

// Load chat history on page load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.messages && data.messages.length > 0) {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
            
            data.messages.forEach(msg => {
                addMessage(msg.content, msg.role);
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
});