import { core } from './modules/core.js';
import { uiManager } from './modules/ui.js';
import { CaseManager } from './modules/cases.js';

// إنشاء نسخة من CaseManager
const caseManager = new CaseManager();

// تخزين مؤقت للمراحل
let tempStages = {};
let currentCaseId = null;
let isAnalyzing = false;

// تعريف الدوال في النطاق العام
window.startAnalysis = async function() {
    const caseText = document.getElementById('caseText')?.value.trim();
    if (!caseText) {
        core.showNotification('يرجى إدخال نص القضية', 'error');
        return;
    }

    try {
        // إظهار إشعار بدء التحليل
        core.showNotification('جاري تحليل القضية...', 'info');
        document.getElementById('analysisResults')?.classList.remove('hidden');
        
        // تحديث حالة جميع المراحل إلى "جاري التحليل"
        for (let i = 1; i <= 5; i++) {
            updateStageStatus(i, 'analyzing');
        }
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: caseText })
        });

        const data = await response.json();
        console.log("Received data:", data); // للتأكد من استلام البيانات

        if (data.error) throw new Error(data.error);

        // تخزين معرف القضية
        currentCaseId = data.case_id;
        
        // عرض نتائج التحليل لكل مرحلة
        Object.entries(data.results).forEach(([stage, result]) => {
            console.log(`Updating stage ${stage}:`, result);
            tempStages[stage] = result;
            updateStageContent(parseInt(stage), result);
        });

        core.showNotification('تم اكتمال التحليل', 'success');
        
        // إظهار زر الحفظ
        document.getElementById('saveCaseBtn')?.classList.remove('hidden');

    } catch (error) {
        console.error("Analysis error:", error);
        core.showNotification(error.message, 'error');
    }
};

window.saveCase = async function() {
    try {
        const response = await fetch('/save-case', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                case_id: currentCaseId,
                text: document.getElementById('caseText').value,
                stages: tempStages
            })
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        core.showNotification('تم حفظ القضية بنجاح', 'success');
        setTimeout(() => {
            window.location.href = '/completed-cases';
        }, 2000);
    } catch (error) {
        core.showNotification(error.message, 'error');
    }
};

function updateStageContent(stageId, content) {
    console.log(`Updating content for stage ${stageId}:`, content);
    
    const stageElement = document.getElementById(`stage${stageId}`);
    if (!stageElement) {
        console.error(`Stage element not found: stage${stageId}`);
        return;
    }

    const contentElement = stageElement.querySelector('.stage-body');
    if (!contentElement) {
        console.error(`Content element not found in stage ${stageId}`);
        return;
    }

    contentElement.innerHTML = `
        <div class="analysis-result">
            <div class="model-info">
                <i class="fas fa-robot"></i>
                تم التحليل باستخدام: ${content.model}
            </div>
            <div class="content-text">
                ${content.content.replace(/\n/g, '<br>')}
            </div>
            <div class="timestamp">
                ${new Date(content.timestamp).toLocaleString('ar-SA')}
            </div>
        </div>
    `;

    stageElement.classList.add('completed');
    updateStageStatus(stageId, 'completed');
}

function updateStageStatus(stageId, status) {
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

function updateProgressBar(stage) {
    const progress = ((stage - 1) / 4) * 100;
    document.getElementById('progressLine').style.width = `${progress}%`;
    
    document.querySelectorAll('.stage-point').forEach((point, index) => {
        point.classList.remove('active', 'completed');
        if (index + 1 < stage) {
            point.classList.add('completed');
        } else if (index + 1 === stage) {
            point.classList.add('active');
        }
    });
}

window.stopAnalysis = function() {
    window.isAnalysisStopped = true;
    core.showNotification('تم إيقاف التحليل', 'info');
};

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.isAnalysisStopped = false;
    window.currentCaseId = null;
    window.currentStage = 1;
});

// دوال مساعدة للتعامل مع النصوص
window.clearText = function() {
    const textarea = document.getElementById('caseText');
    if (textarea) {
        textarea.value = '';
        textarea.focus();
    }
};

window.pasteText = async function() {
    try {
        const text = await navigator.clipboard.readText();
        const textarea = document.getElementById('caseText');
        if (textarea) {
            textarea.value = text;
            textarea.focus();
        }
    } catch (error) {
        console.error('Failed to paste text:', error);
        window.stageManager.showNotification('فشل في لصق النص. يرجى المحاولة يدوياً', 'error');
    }
};

// دوال مساعدة للتنسيق
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('ar-PS', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatMoney(amount) {
    return new Intl.NumberFormat('ar-PS', {
        style: 'currency',
        currency: 'ILS'
    }).format(amount);
}

// دوال مساعدة للتحقق
function validateText(text) {
    if (!text) return false;
    if (text.length < 50) return false;
    return true;
}

// إضافة مستمع لأحداث التحميل
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // تهيئة textarea
    const textarea = document.getElementById('caseText');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});

// معالجة الأخطاء العامة
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    window.stageManager?.showNotification('حدث خطأ غير متوقع', 'error');
}); 