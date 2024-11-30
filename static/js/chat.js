document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');
    const questionButtons = document.querySelectorAll('.question-btn');

    // إضافة مستمعي الأحداث للأزرار
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    questionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            messageInput.value = question;
            sendMessage();
        });
    });

    // دالة إرسال الرسالة
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // إضافة رسالة المستخدم إلى واجهة المستخدم
        appendMessage(message, true);
        messageInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    case_id: getCaseId()
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            appendMessage(data.response, false, data.model);

        } catch (error) {
            console.error('Error:', error);
            appendMessage('عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.', false, 'error');
        }
    }

    // دالة إضافة رسالة إلى واجهة المستخدم
    function appendMessage(content, isUser, model = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = content;

        const messageMeta = document.createElement('div');
        messageMeta.className = 'message-meta';

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString('ar-SA');

        messageMeta.appendChild(timestamp);

        if (!isUser && model) {
            const modelBadge = document.createElement('span');
            modelBadge.className = `model-badge ${model}`;
            modelBadge.innerHTML = `<i class="fas fa-robot"></i> ${model}`;
            messageMeta.appendChild(modelBadge);
        }

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageMeta);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // دالة الحصول على معرف القضية من URL
    function getCaseId() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }
});

// دوال التصدير والمسح
function exportChat() {
    const chatMessages = document.getElementById('chatMessages');
    const case_id = getCaseId();

    fetch(`/api/chat/export/${case_id}`, {
        method: 'GET'
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_export_${case_id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        console.error('Error exporting chat:', error);
        alert('حدث خطأ أثناء تصدير المحادثة');
    });
}

function clearChat() {
    document.getElementById('clearConfirmation').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

function cancelClear() {
    document.getElementById('clearConfirmation').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

function confirmClear() {
    const case_id = getCaseId();
    
    fetch(`/api/chat/clear/${case_id}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('chatMessages').innerHTML = '';
            cancelClear();
        } else {
            throw new Error('Failed to clear chat');
        }
    })
    .catch(error => {
        console.error('Error clearing chat:', error);
        alert('حدث خطأ أثناء مسح المحادثة');
    });
} 