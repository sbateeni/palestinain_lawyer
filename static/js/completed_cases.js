// متغيرات عالمية
let selectedCaseId = null;

// عرض تفاصيل القضية
function viewCase(caseId) {
    window.location.href = `/case/${caseId}`;
}

// حذف قضية
function deleteCase(caseId) {
    selectedCaseId = caseId;
    document.getElementById('deleteConfirmation').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

// إلغاء الحذف
function cancelDelete() {
    selectedCaseId = null;
    document.getElementById('deleteConfirmation').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

// تأكيد الحذف
async function confirmDelete() {
    if (!selectedCaseId) return;
    
    try {
        const response = await fetch(`/delete-case/${selectedCaseId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        // إخفاء نافذة التأكيد
        cancelDelete();
        
        // إعادة تحميل الصفحة
        window.location.reload();
        
    } catch (error) {
        console.error('Error deleting case:', error);
        alert('حدث خطأ أثناء حذف القضية');
    }
}
