const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Timer functionality
let timerDisplay = document.getElementById('timer-display');
let startButton = document.getElementById('start-button');
let pauseButton = document.getElementById('pause-button');
let resetButton = document.getElementById('reset-button');
let endButton = document.getElementById('end-button');
let timerInterval = null;
let remainingSeconds = 0;
let initialSeconds = 0;

// Format time as MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// Parse time from display
function parseTimeFromDisplay() {
    const timeStr = timerDisplay.textContent.trim();
    const [mins, secs] = timeStr.split(':').map(Number);
    return (isNaN(mins) ? 0 : mins) * 60 + (isNaN(secs) ? 0 : secs);
}

// Update display with formatted time
function updateDisplay(seconds) {
    timerDisplay.textContent = formatTime(seconds);
}

// Handle preset time selection
document.querySelectorAll('.preset-time').forEach(button => {
    button.addEventListener('click', function() {
        const minutes = parseInt(this.dataset.minutes);
        initialSeconds = minutes * 60;
        remainingSeconds = initialSeconds;
        updateDisplay(remainingSeconds);
        // Update active state
        document.querySelectorAll('.preset-time').forEach(btn => {
            btn.classList.remove('bg-indigo-100', 'dark:bg-indigo-900', 'text-indigo-600', 'dark:text-indigo-300');
            btn.classList.add('bg-gray-100', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
        });
        this.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
        this.classList.add('bg-indigo-100', 'dark:bg-indigo-900', 'text-indigo-600', 'dark:text-indigo-300');
    });
});

function startTimer() {
    if (timerInterval) return;
    if (initialSeconds === 0) {
        initialSeconds = parseTimeFromDisplay();
    }
    if (remainingSeconds === 0) {
        remainingSeconds = initialSeconds;
    }
    // Create a new session when starting the timer
    const subject = document.getElementById('subject').value;
    const notes = document.getElementById('notes').value;
    fetch('/study_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            subject: subject,
            notes: notes,
            start_time: new Date().toISOString(),
            end_time: null
        })
    })
    .then(response => response.json())
    .then(data => {
        activeSessionId = data.session_id;
        updateEndButtonState();
    })
    .catch(error => {
        console.error('Error creating session:', error);
    });
    timerInterval = setInterval(() => {
        if (remainingSeconds <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            return;
        }
        remainingSeconds--;
        updateDisplay(remainingSeconds);
    }, 1000);
}

function pauseTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function resetTimer() {
    pauseTimer();
    remainingSeconds = 0;
    updateDisplay(initialSeconds || parseTimeFromDisplay());
    initialSeconds = 0;
}

startButton.addEventListener('click', startTimer);
pauseButton.addEventListener('click', pauseTimer);
resetButton.addEventListener('click', resetTimer);

// Progress tracking
let goalHoursInput = document.getElementById('goal-hours');
let progressBar = document.getElementById('progress-bar');
let progressText = document.getElementById('progress-text');
let totalStudyTime = parseFloat(window.total_time_minutes || 0);

function updateProgress() {
    let goalHours = parseFloat(goalHoursInput.value) || 0;
    let timeGoalInMinutes = goalHours * 60;
    let progress = timeGoalInMinutes > 0 ? (totalStudyTime / timeGoalInMinutes) * 100 : 0;
    progress = Math.min(100, progress);
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${Math.round(progress)}% Complete`;
}

goalHoursInput.addEventListener('input', updateProgress);
window.addEventListener('DOMContentLoaded', updateProgress);

// Track active session state
// Function to enable/disable end button
function updateEndButtonState() {
    const endButton = document.getElementById('end-button');
    if (activeSessionId) {
        endButton.classList.remove('opacity-50', 'cursor-not-allowed');
        endButton.disabled = false;
    } else {
        endButton.classList.add('opacity-50', 'cursor-not-allowed');
        endButton.disabled = true;
    }
}

// Check for active session on page load
async function checkActiveSession() {
    try {
        const response = await fetch('/active_session');
        const data = await response.json();
        activeSessionId = data.session_id;
        updateEndButtonState();
    } catch (error) {
        console.error('Error checking active session:', error);
    }
}

// Add end button functionality
async function endTimer() {
    if (!activeSessionId) {
        console.error('No active session to end');
        return;
    }
    if (timerInterval) {
        pauseTimer();
    }
    try {
        const response = await fetch(`/study_session/${activeSessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json', 'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                end_time: new Date().toISOString()
            })
        });
        if (response.ok) {
            activeSessionId = null;
            updateEndButtonState();
            window.location.reload();
        } else {
            console.error('Failed to end session');
        }
    } catch (error) {
        console.error('Error ending session:', error);
    }
}

endButton.addEventListener('click', endTimer);

// Update active session state when starting a new session
const activeSessionForm = document.getElementById('active-session-form');
activeSessionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(activeSessionForm);
    const sessionData = {
        subject: formData.get('subject'),
        notes: formData.get('notes'),
        start_time: new Date().toISOString(),
        end_time: null
    };
    try {
        const response = await fetch('/study_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(sessionData)
        });
        if (response.ok) {
            const data = await response.json();
            activeSessionId = data.session_id;
            updateEndButtonState();
            window.location.reload();
        } else {
            console.error('Failed to save session');
        }
    } catch (error) {
        console.error('Error saving session:', error);
    }
});

// Check for active session when page loads
window.addEventListener('DOMContentLoaded', checkActiveSession);

// Add delete session functionality
let sessionToDelete = null;
let confirmDeleteSessionBtn = document.getElementById('confirmDeleteSession');
let deleteSessionModal = document.getElementById('deleteSessionModal');
let enterListener = null;

function enableEnterToConfirm(modalElement, confirmBtn) {
    function handler(e) {
        if (modalElement.classList.contains('flex') && (e.key === 'Enter' || e.keyCode === 13)) {
            e.preventDefault();
            confirmBtn.click();
        }
    }
    document.addEventListener('keydown', handler);
    // Store for removal
    return handler;
}

function disableEnterToConfirm(handler) {
    document.removeEventListener('keydown', handler);
}

window.showDeleteSessionModal = function(sessionId) {
    sessionToDelete = sessionId;
    const modal = document.getElementById('deleteSessionModal');
    const modalContent = document.getElementById('deleteSessionModalContent');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
    // Enable Enter key for confirm
    enterListener = enableEnterToConfirm(modal, confirmDeleteSessionBtn);
};

function hideDeleteSessionModal() {
    const modal = document.getElementById('deleteSessionModal');
    const modalContent = document.getElementById('deleteSessionModalContent');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
    sessionToDelete = null;
    // Remove Enter key listener
    if (enterListener) {
        disableEnterToConfirm(enterListener);
        enterListener = null;
    }
}

document.getElementById('cancelDeleteSession').addEventListener('click', hideDeleteSessionModal);
document.getElementById('deleteSessionModal').addEventListener('click', function(e) {
    if (e.target === this) hideDeleteSessionModal();
});
document.getElementById('confirmDeleteSession').addEventListener('click', async function() {
    if (!sessionToDelete) return;
    try {
        const response = await fetch(`/study_session/${sessionToDelete}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete session.');
        }
    } catch (error) {
        alert('Error deleting session.');
    } finally {
        hideDeleteSessionModal();
    }
});

// Persistence across reloads
window.addEventListener('beforeunload', () => {
    localStorage.setItem('studyTimer_remainingSeconds', remainingSeconds);
    localStorage.setItem('studyTimer_initialSeconds', initialSeconds);
    localStorage.setItem('studyTimer_startTimestamp', Date.now());
    localStorage.setItem('studyTimer_isRunning', !!timerInterval);
});

window.addEventListener('DOMContentLoaded', () => {
    const savedInitial = parseInt(localStorage.getItem('studyTimer_initialSeconds')) || 0;
    const savedRemaining = parseInt(localStorage.getItem('studyTimer_remainingSeconds')) || 0;
    const wasRunning = localStorage.getItem('studyTimer_isRunning') === 'true';
    const savedTimestamp = parseInt(localStorage.getItem('studyTimer_startTimestamp'));
    if (savedInitial > 0) {
        initialSeconds = savedInitial;
        if (wasRunning && savedTimestamp) {
            const elapsedSeconds = Math.floor((Date.now() - savedTimestamp) / 1000);
            remainingSeconds = Math.max(0, savedRemaining - elapsedSeconds);
            updateDisplay(remainingSeconds);
            if (remainingSeconds > 0) startTimer();
        } else {
            remainingSeconds = savedRemaining;
            updateDisplay(remainingSeconds);
        }
    }
});

let activeSessionId = null;
let sessionActive = false;

const startSessionBtn = document.getElementById('start-session-btn');
const endSessionBtn = document.getElementById('end-session-btn');
const subjectInput = document.getElementById('subject');
const notesInput = document.getElementById('notes');

function updateSessionButtons() {
    if (sessionActive) {
        startSessionBtn.classList.add('opacity-50', 'cursor-not-allowed');
        startSessionBtn.disabled = true;
        endSessionBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        endSessionBtn.disabled = false;
    } else {
        endSessionBtn.classList.add('opacity-50', 'cursor-not-allowed');
        endSessionBtn.disabled = true;
        startSessionBtn.disabled = !subjectInput.value.trim();
        if (startSessionBtn.disabled) {
            startSessionBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            startSessionBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }
}

subjectInput.addEventListener('input', updateSessionButtons);

startSessionBtn.addEventListener('click', async function() {
    if (!subjectInput.value.trim() || sessionActive) return;
    // Start timer logic
    if (typeof timerInterval !== 'undefined' && timerInterval) return;
    if (typeof parseTimeFromDisplay === 'function') {
        initialSeconds = parseTimeFromDisplay();
        remainingSeconds = initialSeconds;
        updateDisplay(remainingSeconds);
        timerInterval = setInterval(() => {
            if (remainingSeconds <= 0) {
                clearInterval(timerInterval);
                timerInterval = null;
                return;
            }
            remainingSeconds--;
            updateDisplay(remainingSeconds);
        }, 1000);
    }
    // Start session in backend
    const subject = subjectInput.value;
    const notes = notesInput.value;
    const response = await fetch('/study_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({
            subject: subject,
            notes: notes,
            start_time: new Date().toISOString(),
            end_time: null
        })
    });
    const data = await response.json();
    activeSessionId = data.session_id;
    sessionActive = true;
    updateSessionButtons();
    // Also enable the main End button if it exists
    if (typeof updateEndButtonState === 'function') {
        updateEndButtonState();
    }
});

endSessionBtn.addEventListener('click', async function() {
    if (!sessionActive || !activeSessionId) return;
    // End timer logic
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    // End session in backend
    await fetch(`/study_session/${activeSessionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ end_time: new Date().toISOString() })
    });
    activeSessionId = null;
    sessionActive = false;
    updateSessionButtons();
    window.location.reload();
});

updateSessionButtons();

function showStartWarning(show) {
    document.getElementById('start-warning').style.display = show ? 'block' : 'none';
}
function showEndWarning(show) {
    document.getElementById('end-warning').style.display = show ? 'block' : 'none';
}

startSessionBtn.addEventListener('mouseenter', function() {
    if (!subjectInput.value.trim() && !sessionActive) showStartWarning(true);
});
startSessionBtn.addEventListener('mouseleave', function() {
    showStartWarning(false);
});
endSessionBtn.addEventListener('mouseenter', function() {
    if (!sessionActive) showEndWarning(true);
});
endSessionBtn.addEventListener('mouseleave', function() {
    showEndWarning(false);
});

endButton.addEventListener('mouseenter', function() {
    if (!activeSessionId) document.getElementById('timer-end-warning').style.display = 'block';
});
endButton.addEventListener('mouseleave', function() {
    document.getElementById('timer-end-warning').style.display = 'none';
});

// Add show/hide notes functionality for recent sessions
document.querySelectorAll('.show-notes-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const sessionId = this.getAttribute('data-session-id');
        const notesDiv = document.getElementById('notes-' + sessionId);
        if (notesDiv) {
            notesDiv.classList.toggle('hidden');
        }
    });
}); 