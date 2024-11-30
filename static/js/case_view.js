// متغيرات عالمية
let selectedCaseId = null;

// دالة تصدير القضية إلى PDF
async function exportCase() {
    try {
        const caseId = window.location.pathname.split('/').pop();
        const response = await fetch(`/api/chat/export/${caseId}`);
        
        if (!response.ok) {
            throw new Error('فشل تصدير القضية');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `case-${caseId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error('Error exporting case:', error);
        alert('حدث خطأ أثناء تصدير القضية');
    }
}

// دالة حذف القضية
async function deleteCase() {
    if (!confirm('هل أنت متأكد من حذف هذه القضية؟')) {
        return;
    }

    try {
        const caseId = window.location.pathname.split('/').pop();
        const response = await fetch(`/delete-case/${caseId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('فشل حذف القضية');
        }

        const data = await response.json();
        alert(data.message);
        window.location.href = '/completed-cases';
        
    } catch (error) {
        console.error('Error deleting case:', error);
        alert('حدث خطأ أثناء حذف القضية');
    }
} 