// JavaScript for the Assessments page
// Backend-integrated assessments array
let assessments = [];
let editingId = null;
let deleteModalOpen = false;

async function fetchAssessments() {
    const res = await fetch('/main/api/assessments');
    assessments = await res.json();
    renderAssessments();
}

function renderAssessments() {
    const list = document.getElementById('assessmentsList');
    const empty = document.getElementById('emptyState');
    list.innerHTML = '';
    if (assessments.length === 0) {
        empty.classList.remove('hidden');
        return;
    } else {
        empty.classList.add('hidden');
    }
    // Group by subject
    const grouped = {};
    assessments.forEach(a => {
        if (!grouped[a.subject]) grouped[a.subject] = [];
        grouped[a.subject].push(a);
    });
    Object.entries(grouped).forEach(([subject, subjectAssessments]) => {
        // Calculate weighted average grade for completed assessments
        let totalWeight = 0;
        let weightedSum = 0;
        subjectAssessments.forEach(a => {
            const gradeValid = typeof a.grade === 'number' && !isNaN(a.grade);
            const weightValid = typeof a.weight === 'number' && !isNaN(a.weight) && a.weight > 0;
            if (a.done && gradeValid && weightValid) {
                weightedSum += a.grade * a.weight;
                totalWeight += a.weight;
            }
        });
        let gradeDisplay = '—';
        if (totalWeight > 0) {
            gradeDisplay = (weightedSum / totalWeight).toFixed(2) + '%';
        }
        // Subject card
        const subjectCard = document.createElement('div');
        subjectCard.className = 'bg-white dark:bg-gray-700 rounded-2xl shadow-lg p-6 border border-gray-100 dark:border-gray-600 mb-6';
        subjectCard.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center mr-4">
                        <i class="fas fa-book text-xl text-indigo-600 dark:text-indigo-300"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">${subject}</h2>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-500 dark:text-gray-300">Current Grade:</span>
                    <span class="text-xl font-bold text-indigo-600 dark:text-indigo-300" title="Weighted average of completed assessments with grade and weight">${gradeDisplay}</span>
                </div>
            </div>
            <div class="space-y-4" id="subject-assessments-${subject.replace(/[^a-zA-Z0-9]/g, '')}"></div>
        `;
        list.appendChild(subjectCard);
        // Render assessments for this subject
        const subjectList = subjectCard.querySelector(`#subject-assessments-${subject.replace(/[^a-zA-Z0-9]/g, '')}`);
        subjectAssessments.forEach(a => {
            const card = document.createElement('div');
            card.className = 'bg-gray-50 dark:bg-gray-800 rounded-xl p-4 flex flex-col justify-between shadow-sm border border-gray-100 dark:border-gray-600';
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">${a.title}</h3>
                        <span class="text-sm text-gray-500 dark:text-gray-400">Due: <span class="font-medium text-gray-900 dark:text-white">${a.due_date}</span></span>
                        <div class="flex gap-4 mt-1">
                            <span class="text-xs text-gray-500 dark:text-gray-400">Grade: <span class="font-semibold text-gray-900 dark:text-white">${a.grade !== null && a.grade !== undefined && a.grade !== '' ? Number(a.grade).toFixed(2) + '%' : '—'}</span></span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">Weight: <span class="font-semibold text-gray-900 dark:text-white">${a.weight !== null && a.weight !== undefined && a.weight !== '' ? Number(a.weight).toFixed(2) + '%' : '—'}</span></span>
                        </div>
                    </div>
                    <span class="inline-block px-3 py-1 text-xs rounded-full ${a.done ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'} font-semibold">${a.done ? 'Completed' : 'Upcoming'}</span>
                </div>
                <div class="flex justify-end gap-2 mt-2">
                    <button class="px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm font-medium transition-colors duration-200" title="${a.done ? 'Mark as Upcoming' : 'Mark as Done'}" onclick="markDone('${a.id}')">
                        <i class="fas ${a.done ? 'fa-rotate-left' : 'fa-check'}"></i>
                    </button>
                    <button class="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm font-medium transition-colors duration-200" title="Edit" onclick="editAssessment('${a.id}')"><i class="fas fa-edit"></i></button>
                    <button class="px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm font-medium transition-colors duration-200" title="Delete" onclick="showDeleteModal('${a.id}')"><i class="fas fa-trash"></i></button>
                </div>
            `;
            subjectList.appendChild(card);
        });
    });
}

function showAssessmentModal(editId = null) {
    const modal = document.getElementById('assessmentModal');
    const content = document.getElementById('assessmentModalContent');
    document.getElementById('assessmentForm').reset();
    document.getElementById('assessmentId').value = '';
    document.getElementById('modalTitle').textContent = editId ? 'Edit Assessment' : 'Add Assessment';
    if (editId) {
        const a = assessments.find(x => x.id == editId);
        if (a) {
            document.getElementById('assessmentId').value = a.id;
            document.getElementById('subject').value = a.subject;
            document.getElementById('title').value = a.title;
            document.getElementById('dueDate').value = a.due_date;
            document.getElementById('grade').value = a.grade != null ? a.grade : '';
            document.getElementById('weight').value = a.weight != null ? a.weight : '';
        }
    }
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function hideAssessmentModal() {
    const modal = document.getElementById('assessmentModal');
    const content = document.getElementById('assessmentModalContent');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
}

function showDeleteModal(id) {
    deleteModalOpen = true;
    document.getElementById('deleteModal').classList.remove('hidden');
    document.getElementById('deleteModal').classList.add('flex');
    document.getElementById('confirmDeleteBtn').setAttribute('data-id', id);
    setTimeout(() => {
        document.getElementById('deleteModalContent').classList.remove('scale-95', 'opacity-0');
        document.getElementById('deleteModalContent').classList.add('scale-100', 'opacity-100');
    }, 10);
}

function hideDeleteModal() {
    deleteModalOpen = false;
    const modal = document.getElementById('deleteModal');
    const content = document.getElementById('deleteModalContent');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
}

async function markDone(id) {
    const a = assessments.find(x => x.id == id);
    if (a) {
        await fetch(`/main/api/assessments/${a.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ done: !a.done })
        });
        await fetchAssessments();
    }
}

function editAssessment(id) {
    showAssessmentModal(id);
}

// Event Listeners

document.getElementById('addAssessmentBtn').addEventListener('click', () => showAssessmentModal());
document.getElementById('emptyAddBtn').addEventListener('click', () => showAssessmentModal());
document.getElementById('cancelModalBtn').addEventListener('click', hideAssessmentModal);
document.getElementById('assessmentModal').addEventListener('click', function(e) {
    if (e.target === this) hideAssessmentModal();
});
document.getElementById('assessmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const id = document.getElementById('assessmentId').value;
    const subject = document.getElementById('subject').value.trim();
    const title = document.getElementById('title').value.trim();
    const due_date = document.getElementById('dueDate').value;
    const grade = document.getElementById('grade').value;
    const weight = document.getElementById('weight').value;
    if (!subject || !title || !due_date) return;

    // --- Weight validation ---
    const newWeight = weight !== '' ? parseFloat(weight) : 0;
    let totalWeight = 0;
    assessments.forEach(a => {
        if (a.subject === subject && a.id != id && typeof a.weight === 'number' && !isNaN(a.weight)) {
            totalWeight += a.weight;
        }
    });
    if (newWeight + totalWeight > 100) {
        showWarningModal('Total weight for this subject cannot exceed 100%.');
        return;
    }
    // --- End weight validation ---

    const payload = { subject, title, due_date };
    if (grade !== '') payload.grade = parseFloat(grade);
    if (weight !== '') payload.weight = parseFloat(weight);
    if (id) {
        // Update
        await fetch(`/main/api/assessments/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } else {
        // Create
        await fetch('/main/api/assessments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    }
    hideAssessmentModal();
    await fetchAssessments();
});

document.getElementById('cancelDeleteBtn').addEventListener('click', hideDeleteModal);
document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) hideDeleteModal();
});
document.getElementById('confirmDeleteBtn').addEventListener('click', async function() {
    const id = this.getAttribute('data-id');
    await fetch(`/main/api/assessments/${id}`, { method: 'DELETE' });
    hideDeleteModal();
    await fetchAssessments();
});

document.addEventListener('keydown', function(e) {
    if (deleteModalOpen) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('confirmDeleteBtn').click();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            hideDeleteModal();
        }
    }
});

function showWarningModal(message) {
    document.getElementById('warningModalMessage').textContent = message;
    const modal = document.getElementById('warningModal');
    const content = document.getElementById('warningModalContent');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function hideWarningModal() {
    const modal = document.getElementById('warningModal');
    const content = document.getElementById('warningModalContent');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
}

document.getElementById('closeWarningBtn').addEventListener('click', hideWarningModal);
document.getElementById('warningModal').addEventListener('click', function(e) {
    if (e.target === this) hideWarningModal();
});
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('warningModal');
    if (!modal.classList.contains('hidden') && (e.key === 'Enter' || e.key === 'Escape')) {
        hideWarningModal();
    }
});

// Initial fetch
fetchAssessments(); 