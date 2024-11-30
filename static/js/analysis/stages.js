class StageManager {
    constructor() {
        this.currentStage = 0;
        this.tempStages = {};
        this.isAnalyzing = false;
        this.currentCaseId = null;
    }

    async startAnalysis() {
        const caseText = document.getElementById('caseText')?.value.trim();
        if (!caseText) {
            this.showNotification('يرجى إدخال نص القضية', 'error');
            return;
        }

        if (this.isAnalyzing) {
            this.showNotification('جاري التحليل بالفعل', 'info');
            return;
        }

        try {
            this.isAnalyzing = true;
            document.getElementById('analysisResults')?.classList.remove('hidden');
            
            // تحليل المراحل الثمانية
            for (let stage = 1; stage <= 8; stage++) {
                this.showNotification(`جاري تحليل المرحلة ${stage}...`, 'info');
                this.updateStageStatus(stage, 'analyzing');

                const response = await fetch(`/analyze-stage/${stage}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        text: caseText,
                        case_id: this.currentCaseId
                    })
                });

                const data = await response.json();
                if (data.error) throw new Error(data.error);

                // تخزين نتيجة المرحلة
                this.tempStages[stage] = data.result;
                this.updateStageContent(stage, data.result);
                this.showNotification(`تم إكمال المرحلة ${stage}`, 'success');

                // انتظار قبل بدء المرحلة التالية
                if (stage < 8) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }

            // إظهار زر الحفظ
            document.getElementById('saveCaseBtn')?.classList.remove('hidden');
            this.showNotification('تم اكتمال جميع مراحل التحليل', 'success');

        } catch (error) {
            console.error("Analysis error:", error);
            this.showNotification(error.message, 'error');
        } finally {
            this.isAnalyzing = false;
        }
    }

    updateStageContent(stageId, content) {
        console.log(`Updating content for stage ${stageId}:`, content);
        
        const stageElement = document.getElementById(`stage${stageId}`);
        if (!stageElement) return;

        const contentElement = stageElement.querySelector('.stage-body');
        contentElement.innerHTML = `
            <div class="analysis-result">
                <div class="model-info">
                    <i class="fas fa-robot"></i>
                    تم التحليل باستخدام: ${content.model}
                </div>
                <div class="content-text">
                    ${String(content.content || '').replace(/\n/g, '<br>')}
                </div>
                <div class="timestamp">
                    ${new Date(content.timestamp).toLocaleString('ar-SA')}
                </div>
            </div>
        `;

        stageElement.classList.add('completed');
        this.updateStageStatus(stageId, 'completed');
    }

    updateStageStatus(stageId, status) {
        const statusElement = document.querySelector(`#stage${stageId} .stage-status`);
        if (statusElement) {
            let html = '';
            switch(status) {
                case 'analyzing':
                    html = '<i class="fas fa-spinner fa-spin"></i> جاري التحليل...';
                    break;
                case 'completed':
                    html = '<i class="fas fa-check-circle"></i> تم التحليل';
                    break;
                default:
                    html = '<i class="fas fa-clock"></i> في الانتظار...';
            }
            statusElement.innerHTML = html;
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    async saveCase() {
        try {
            // تحضير بيانات المراحل
            const formattedStages = {};
            for (const [stage, data] of Object.entries(this.tempStages)) {
                formattedStages[stage] = {
                    content: data,
                    status: 'completed',
                    model: parseInt(stage) % 2 === 1 ? 'groq' : 'gemini',
                    timestamp: new Date().toISOString()
                };
            }

            const response = await fetch('/save-case', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    stages: formattedStages,
                    text: document.getElementById('caseText')?.value.trim()
                })
            });

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            // تحديث معرف القضية بعد الحفظ
            this.currentCaseId = data.case_id;
            
            // إطلاق حدث حفظ القضية
            const event = new CustomEvent('caseSaved', {
                detail: {
                    caseId: this.currentCaseId
                }
            });
            document.dispatchEvent(event);

            this.showNotification('تم حفظ القضية بنجاح', 'success');
            
            // إظهار قسم المحادثة
            document.getElementById('chat-section').style.display = 'block';

            // تحديث URL الصفحة
            window.history.pushState({}, '', `/case/${data.case_id}`);

        } catch (error) {
            console.error('Error saving case:', error);
            this.showNotification(error.message, 'error');
        }
    }
}

// إنشاء نسخة عالمية
window.stageManager = new StageManager();

// تعريف دالة saveCase العالمية
window.saveCase = function() {
    window.stageManager.saveCase();
};

// إدارة الدردشة
class ChatManager {
    constructor() {
        this.chatSection = document.getElementById('chat-section');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-message');
        this.exportButton = document.getElementById('export-chat');
        
        this.currentCaseId = null;
        this.initialize();
    }
    
    initialize() {
        // إظهار قسم الدردشة بعد اكتمال المرحلة 8
        document.addEventListener('analysisCompleted', (event) => {
            if (event.detail.stage === 8) {
                this.currentCaseId = event.detail.caseId;
                this.chatSection.style.display = 'block';
                this.loadChatHistory();
            }
        });

        // الاستماع لحدث حفظ القضية
        document.addEventListener('caseSaved', (event) => {
            this.currentCaseId = event.detail.caseId;
        });
        
        // إضافة مستمعي الأحداث
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.exportButton.addEventListener('click', () => this.exportChat());

        // معالجة الأسئلة المقترحة
        document.querySelectorAll('.question-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.dataset.question;
                if (question) {
                    this.chatInput.value = question;
                    this.sendMessage();
                }
            });
        });
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        if (!this.currentCaseId) {
            this.showNotification('يجب حفظ القضية أولاً قبل بدء المحادثة', 'error');
            return;
        }
        
        // إضافة رسالة المستخدم
        this.addMessageToChat(message, 'user');
        this.chatInput.value = '';
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    case_id: this.currentCaseId,
                    message: message
                })
            });
            
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            // إضافة رد النظام
            this.addMessageToChat(data.response, 'bot');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessageToChat('عذراً، حدث خطأ في معالجة رسالتك. يرجى المحاولة مرة أخرى.', 'bot', true);
        }
    }
    
    addMessageToChat(message, type, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}-message`;
        if (isError) messageDiv.classList.add('error-message');
        
        messageDiv.textContent = message;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`/chat-history/${this.currentCaseId}`);
            const data = await response.json();
            
            // مسح الرسائل الحالية
            this.chatMessages.innerHTML = '';
            
            // إضافة الرسائل السابقة
            data.messages.forEach(msg => {
                this.addMessageToChat(msg.message, 'user');
                this.addMessageToChat(msg.response, 'bot');
            });
            
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async exportChat() {
        try {
            const response = await fetch(`/export-chat/${this.currentCaseId}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-history-${this.currentCaseId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting chat:', error);
            alert('عذراً، حدث خطأ أثناء تصدير المحادثة');
        }
    }
}

// تهيئة مدير الدردشة
const chatManager = new ChatManager();