// Global variables
let moodChart = null;
let pendingDeleteId = null;

// <<<<<<< HEAD
// Water Reminder Functionality
let waterReminderInterval = null;
let snoozeTimeout = null;

// Modal elements
const waterReminderModal = document.getElementById('waterReminderModal');
const waterModalContent = document.getElementById('waterModalContent');
const waterModalSnooze = document.getElementById('waterModalSnooze');
const waterModalDismiss = document.getElementById('waterModalDismiss');

// Form elements
const waterReminderForm = document.getElementById('waterReminderForm');
const startReminderBtn = document.getElementById('startReminder');
const stopReminderBtn = document.getElementById('stopReminder');

// Water Tracking Functionality
const WATER_STORAGE_KEY = 'waterTrackerData';
// Define the cup capacity in liters and milliliters
let CUP_CAPACITY_LITERS = 2.0;
let CUP_CAPACITY_ML = CUP_CAPACITY_LITERS * 1000;
const ENCOURAGING_MESSAGES = [
    "You're doing great! Keep hydrating! 💧",
    "Every sip counts towards your goal! 🌊",
    "Stay hydrated, stay healthy! 💪",
    "You're on track to reach your goal! 🎯",
    "Keep up the good work! 🌟",
    "Your body thanks you for staying hydrated! 💫",
    "You're making waves with your hydration! 🌊",
    "Almost there! Keep going! ⭐",
    "You're crushing your water goals! 🏆",
    "Stay refreshed, stay focused! 💫"
];

// Water tracking elements
const waterGoal = document.getElementById('waterGoal');
const waterLevel = document.getElementById('waterLevel');
const waterFill = document.getElementById('waterFill');
const splashEffect = document.getElementById('splashEffect');
const waterProgressMessage = document.getElementById('waterProgressMessage');
const waterAmount = document.getElementById('waterAmount');
const addWaterBtn = document.getElementById('addWater');
const undoWaterBtn = document.getElementById('undoWater');
const resetWaterBtn = document.getElementById('resetWater');
const toggleReminderSettings = document.getElementById('toggleReminderSettings');
const reminderSettings = document.getElementById('reminderSettings');

// Water tracking state
let waterData = {
    current: 0, // in milliliters
    goal: 2000, // default 2L in milliliters
    history: [],
    lastUpdated: new Date().toISOString().split('T')[0]
};
// =======
// function toAWST(dateString) {
//     const date = new Date(dateString);
//     const options = {
//         timeZone: 'Australia/Perth',
//         year: 'numeric',
//         month: '2-digit',
//         day: '2-digit',
//         hour: '2-digit',
//         minute: '2-digit',
//         hour12: false
//     };
//     const parts = new Intl.DateTimeFormat('en-CA', options).formatToParts(date);
//     const y = parts.find(p => p.type === 'year').value;
//     const m = parts.find(p => p.type === 'month').value;
//     const d = parts.find(p => p.type === 'day').value;
//     const h = parts.find(p => p.type === 'hour').value;
//     const min = parts.find(p => p.type === 'minute').value;
//     return `${y}-${m}-${d} ${h}:${min}`;
// }
// >>>>>>> ce1efbc2c0c59ebf8757dc8f446616729fab22ce

function showConfirmationModal(entryId) {
    const modal = document.getElementById('confirmationModal');
    const modalContent = document.getElementById('modalContent');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    // Show modal content with animation
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
    pendingDeleteId = entryId;
}

function hideConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    const modalContent = document.getElementById('modalContent');
    // Hide modal content with animation
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
    modal.classList.add('hidden');
    }, 200);
    pendingDeleteId = null;
}

function deleteEntry(entryId) {
    showConfirmationModal(entryId);
}

function confirmDelete() {
    if (!pendingDeleteId) return;

    fetch(`/api/mood_entries/${pendingDeleteId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete entry');
        }
        // Remove the entry from the DOM
        const entryElement = document.getElementById(`entry-${pendingDeleteId}`);
        if (entryElement) {
            entryElement.remove();
        }
        // Refresh the chart data
        return fetch('/api/mood_entries');
    })
    .then(response => response.json())
    .then(entries => {
        if (!moodChart) return; // Guard clause if chart isn't initialized
        
        // Update chart data
        const moodData = new Array(7).fill(null);
        entries.forEach(entry => {
            const date = new Date(entry.created_at);
            const dayIndex = date.getDay();
            moodData[dayIndex] = entry.mood_score;
        });

        moodChart.data.datasets[0].data = moodData;
        moodChart.update();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete entry. Please try again.');
    })
    .finally(() => {
        hideConfirmationModal();
    });
}

function addEntryToList(entry) {
    const entriesDiv = document.getElementById('recentEntries');
    const entryElement = document.createElement('div');
    entryElement.className = 'bg-gray-50 dark:bg-gray-600 rounded-xl p-6 hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors duration-200';
    entryElement.id = `entry-${entry.id}`;
    entryElement.innerHTML = `
        <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-4">
                <div class="w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                    <i class="fas fa-user text-xl text-indigo-600 dark:text-indigo-300"></i>
                </div>
            <div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">${toAWST(entry.created_at)}</p>
                    <div class="flex items-center space-x-4 mt-1">
                        <div class="flex items-center">
                            <i class="fas fa-face-smile text-indigo-600 dark:text-indigo-300 mr-2"></i>
                            <span class="font-medium text-gray-900 dark:text-white">${entry.mood_score}/10</span>
                        </div>
                    </div>
                </div>
            </div>
            <button onclick="deleteEntry('${entry.id}')"
                class="text-red-600 hover:text-red-800 transition-colors duration-200">
                <i class="fas fa-trash-alt text-lg"></i>
                </button>
            </div>
        ${entry.reflection ? `
        <div class="mt-4 p-4 bg-white dark:bg-gray-700 rounded-xl overflow-x-auto break-words" style="overflow-wrap: break-word; word-break: break-word;">
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed break-words" style="overflow-wrap: break-word; word-break: break-word;">${entry.reflection}</p>
        </div>
        ` : ''}
    `;
    entriesDiv.insertBefore(entryElement, entriesDiv.firstChild);
}

document.addEventListener('DOMContentLoaded', function() {
    // Set waterGoal select value to current capacity on page load
    waterGoal.value = CUP_CAPACITY_LITERS.toString();

    // Retrieve and populate goal inputs from localStorage
    const goalInputsLocal = document.querySelectorAll('.goal-input');
    goalInputsLocal.forEach((input, index) => {
        const storedValue = localStorage.getItem(`goalInput${index}`);
        if (storedValue) {
            input.value = storedValue;
        }
        input.addEventListener('input', () => {
            localStorage.setItem(`goalInput${index}`, input.value);
        });
    });
    // Retrieve and populate goal inputs from localStorage
    const goalInputs = document.querySelectorAll('.goal-input');
    goalInputs.forEach((input, index) => {
        const storedValue = localStorage.getItem(`goalInput${index}`);
        if (storedValue) {
            input.value = storedValue;
        }
        input.addEventListener('input', () => {
            localStorage.setItem(`goalInput${index}`, input.value);
        });
    });
    // Retrieve and populate goal checkboxes from localStorage
    const goalCheckboxes = document.querySelectorAll('.goal-input');
    goalInputs.forEach((input, index) => {
        const storedValue = localStorage.getItem(`goalCheckbox${index}`);
        if (storedValue) {
            input.checked = storedValue === 'true';
        }
        input.addEventListener('change', () => {
            localStorage.setItem(`goalCheckbox${index}`, input.checked);
        });
    });
    // Retrieve and populate goal inputs from localStorage
    goalCheckboxes.forEach((input, index) => {
        const storedValue = localStorage.getItem(`goalInput${index}`);
        if (storedValue) {
            input.value = storedValue;
        }
        input.addEventListener('input', () => {
            localStorage.setItem(`goalInput${index}`, input.value);
        });
    });
    // Mood slider value display
    const moodSlider = document.getElementById('mood');
    const moodValue = document.getElementById('moodValue');

    // Set initial values
    moodSlider.value = 5;
    moodValue.textContent = '5';

    moodSlider.addEventListener('input', function() {
        moodValue.textContent = this.value;
    });

    // Initialize mood chart
    const ctx = document.getElementById('moodChart').getContext('2d');
    moodChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Mood',
                data: [7, 6, 8, 7, 9, 8, 7],
                borderColor: '#4F46E5',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10
                }
            }
        }
    });

    // Form submission
    document.getElementById('moodForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const data = {
            mood_score: parseInt(moodSlider.value),
            reflection: document.getElementById('reflection').value
        };

        // Add date if provided
        const entryDate = document.getElementById('entry_date').value;
        if (entryDate) {
            data.created_at = new Date(entryDate).toISOString();
        }

        fetch('/api/mood_entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(entry => {
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to save entry. Please try again.');
        });
    });

    // Load initial data for the chart
    fetch('/api/mood_entries')
        .then(response => response.json())
        .then(entries => {
            // Process entries for the chart
            const moodData = new Array(7).fill(null);
            entries.forEach(entry => {
                const date = new Date(entry.created_at);
                const dayIndex = date.getDay();
                moodData[dayIndex] = entry.mood_score;
            });
            // Update chart data
            moodChart.data.datasets[0].data = moodData;
            moodChart.update();
        })
        .catch(error => console.error('Error loading mood entries:', error));

    // Add event listeners for modal buttons
    document.getElementById('modalCancel').addEventListener('click', hideConfirmationModal);
    document.getElementById('modalConfirm').addEventListener('click', confirmDelete);

    // Close modal when clicking outside
    document.getElementById('confirmationModal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideConfirmationModal();
        }
    });

    // Water tracking event listeners
    addWaterBtn.addEventListener('click', addWater);
    undoWaterBtn.addEventListener('click', undoWater);
    resetWaterBtn.addEventListener('click', resetWater);
    waterGoal.addEventListener('change', updateGoal);
    
    function updateGoal() {
        const selectedValue = parseFloat(waterGoal.value);
        if (selectedValue < 0.5) {
            waterGoal.value = "0.5";
            CUP_CAPACITY_LITERS = 0.5;
        } else if (selectedValue > 4.0) {
            waterGoal.value = "4.0";
            CUP_CAPACITY_LITERS = 4.0;
        } else {
            CUP_CAPACITY_LITERS = selectedValue;
        }
        CUP_CAPACITY_ML = CUP_CAPACITY_LITERS * 1000;
        waterData.goal = CUP_CAPACITY_ML;  // Update waterData goal to match selected daily water goal
        updateWaterDisplay();
    }
    toggleReminderSettings.addEventListener('click', toggleSettings);

    // Load initial water data
    loadWaterData();
});

// =====================
// Share Data Page Logic
// =====================

function showModal(title, message) {
    const modal = document.getElementById('customModal');
    const modalContent = document.getElementById('modalContent');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Trigger animation
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('customModal');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
}

function shareData() {
    const dataToShare = {
        study_progress: document.getElementById('shareStudyProgress').checked,
        mood: document.getElementById('shareMood').checked,
        tasks: document.getElementById('shareTasks').checked
    };

    // Get selected friends
    const selectedFriends = Array.from(document.querySelectorAll('.friend-checkbox:checked')).map(checkbox => checkbox.id.replace('friend_', ''));

    // Check if any data is selected
    if (!dataToShare.study_progress && !dataToShare.mood && !dataToShare.tasks && !dataToShare.water) {
        showModal('No Data Selected', 'Please select at least one type of data to share.');
        return;
    }

    // Check if any friends are selected
    if (selectedFriends.length === 0) {
        showModal('No Friends Selected', 'Please select at least one friend to share with.');
        return;
    }

    // Share with each selected friend
    const sharePromises = selectedFriends.map(friendId => 
        fetch('/api/share_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                friend_id: friendId,
                data: dataToShare
            })
        }).then(response => response.json())
    );

    Promise.all(sharePromises)
        .then(results => {
            const allSuccessful = results.every(result => result.success);
            if (allSuccessful) {
                showModal('Success', 'Data shared successfully with all selected friends!');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showModal('Error', 'Error sharing data with some friends. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal('Error', 'Error sharing data. Please try again.');
        });
}

// Close modal when clicking outside
if (document.getElementById('customModal')) {
    document.getElementById('customModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Show modal with animation
function showWaterReminderModal() {
    waterReminderModal.classList.remove('hidden');
    waterReminderModal.classList.add('flex');
    setTimeout(() => {
        waterModalContent.classList.remove('scale-95', 'opacity-0');
        waterModalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

// Hide modal with animation
function hideWaterReminderModal() {
    waterModalContent.classList.remove('scale-100', 'opacity-100');
    waterModalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        waterReminderModal.classList.remove('flex');
        waterReminderModal.classList.add('hidden');
    }, 300);
}

// Start the water reminder timer
function startWaterReminder(hours, minutes) {
    const totalMilliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000);
    
    // Clear any existing intervals
    if (waterReminderInterval) {
        clearInterval(waterReminderInterval);
    }
    
    // Set up the interval
    waterReminderInterval = setInterval(() => {
        showWaterReminderModal();
    }, totalMilliseconds);
    
    // Show first reminder after the interval
    setTimeout(() => {
        showWaterReminderModal();
    }, totalMilliseconds);
    
    // Update UI
    startReminderBtn.classList.add('hidden');
    stopReminderBtn.classList.remove('hidden');
}

// Stop the water reminder timer
function stopWaterReminder() {
    if (waterReminderInterval) {
        clearInterval(waterReminderInterval);
        waterReminderInterval = null;
    }
    if (snoozeTimeout) {
        clearTimeout(snoozeTimeout);
        snoozeTimeout = null;
    }
    
    // Update UI
    startReminderBtn.classList.remove('hidden');
    stopReminderBtn.classList.add('hidden');
}

// Event Listeners
// --- Study Break Timer Feature ---

let studyBreakInterval = null;
let studyBreakRemaining = 0;
const studyBreakTimerDisplay = document.getElementById('studyBreakTimerDisplay');
const studyBreakHours = document.getElementById('studyBreakHours');
const studyBreakMinutes = document.getElementById('studyBreakMinutes');
const startStudyBreakReminder = document.getElementById('startStudyBreakReminder');
const studyBreakIdeasDiv = document.getElementById('studyBreakIdeas');

const studyBreakIdeas = [
    "Take a deep breath and stretch your arms!",
    "Do 10 jumping jacks.",
    "Look out the window for 1 minute.",
    "Try a quick breathing exercise.",
    "Walk around your room.",
    "Drink a glass of water.",
    "Write down one thing you're grateful for.",
    "Do a quick doodle.",
    "Listen to your favorite song.",
    "Close your eyes and relax your face muscles."
];

let studyBreakIdeaIndex = 0;
let studyBreakIdeaInterval = null;

function updateStudyBreakTimerDisplay() {
    const minutes = Math.floor(studyBreakRemaining / 60);
    const seconds = studyBreakRemaining % 60;
    studyBreakTimerDisplay.textContent = 
        minutes.toString().padStart(2, '0') + ':' + 
        seconds.toString().padStart(2, '0');
}

function startStudyBreakTimer() {
    // Get user input
    const hours = parseInt(studyBreakHours.value, 10);
    const minutes = parseInt(studyBreakMinutes.value, 10);
    studyBreakRemaining = hours * 60 * 60 + minutes * 60;

    if (studyBreakInterval) clearInterval(studyBreakInterval);

    updateStudyBreakTimerDisplay();

    studyBreakInterval = setInterval(() => {
        if (studyBreakRemaining > 0) {
            studyBreakRemaining--;
            updateStudyBreakTimerDisplay();
        } else {
            clearInterval(studyBreakInterval);
            studyBreakInterval = null;
            // Notify user (simple alert, can be replaced with modal)
            alert("Time for a study break!");
            // Optionally, reset timer display
            updateStudyBreakTimerDisplay();
        }
    }, 1000);
}

// Rotate study break ideas every 15 seconds
function rotateStudyBreakIdeas() {
    studyBreakIdeaIndex = (studyBreakIdeaIndex + 1) % studyBreakIdeas.length;
    studyBreakIdeasDiv.innerHTML = "<span>" + studyBreakIdeas[studyBreakIdeaIndex] + "</span>";
}

if (startStudyBreakReminder) {
    startStudyBreakReminder.addEventListener('click', startStudyBreakTimer);
}

// Start rotating ideas
if (studyBreakIdeasDiv) {
    studyBreakIdeaInterval = setInterval(rotateStudyBreakIdeas, 15000);
}
waterReminderForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const hours = parseInt(document.getElementById('hours').value);
    const minutes = parseInt(document.getElementById('minutes').value);
    
    // Validate that at least one time unit is greater than 0
    if (hours === 0 && minutes === 0) {
        alert('Please select a time interval greater than 0');
        return;
    }
    
    startWaterReminder(hours, minutes);
});

stopReminderBtn.addEventListener('click', () => {
    stopWaterReminder();
});

waterModalSnooze.addEventListener('click', () => {
    hideWaterReminderModal();
    // Snooze for 5 minutes
    snoozeTimeout = setTimeout(() => {
        showWaterReminderModal();
    }, 5 * 60 * 1000);
});

waterModalDismiss.addEventListener('click', () => {
    hideWaterReminderModal();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (waterReminderInterval) {
        clearInterval(waterReminderInterval);
    }
    if (snoozeTimeout) {
        clearTimeout(snoozeTimeout);
    }
});

// Load water data from localStorage
function loadWaterData() {
    const savedData = localStorage.getItem(WATER_STORAGE_KEY);
    if (savedData) {
        const parsed = JSON.parse(savedData);
        // Check if the saved data is from today
        if (parsed.lastUpdated === new Date().toISOString().split('T')[0]) {
            waterData = parsed;
        } else {
            // Reset for new day
            waterData = {
                current: 0,
                goal: parsed.goal,
                history: [],
                lastUpdated: new Date().toISOString().split('T')[0]
            };
        }
    }
    updateWaterDisplay();
}

// Save water data to localStorage
function saveWaterData() {
    localStorage.setItem(WATER_STORAGE_KEY, JSON.stringify(waterData));
}

// Show splash animation
function showSplashAnimation() {
    splashEffect.style.opacity = '1';
    splashEffect.style.transform = 'translateY(-10px)';
    setTimeout(() => {
        splashEffect.style.opacity = '0';
        splashEffect.style.transform = 'translateY(0)';
    }, 500);
}

// Get random encouraging message
function getEncouragingMessage(progress) {
    if (progress >= 100) {
        return '🎉 Well done! You\'ve reached your daily water intake goal!';
    }
    const index = Math.floor(Math.random() * ENCOURAGING_MESSAGES.length);
    return ENCOURAGING_MESSAGES[index];
}

// Update water display
function updateWaterDisplay() {
    const progress = (waterData.current / waterData.goal) * 100;
    const progressLimited = Math.min(progress, 100);
    
    // Update water fill with splash animation
    const currentHeight = waterFill.style.height;
    waterFill.style.height = `${progressLimited}%`;
    if (currentHeight !== waterFill.style.height) {
        showSplashAnimation();
    }
    
    // Update water level text
    const currentLiters = (waterData.current / 1000).toFixed(1);
    waterLevel.textContent = `${currentLiters}L`;
    
    // Update progress message
    waterProgressMessage.innerHTML = getEncouragingMessage(progress);
    
    // Update undo button state
    undoWaterBtn.disabled = waterData.history.length === 0;
    
    // Save to localStorage
    saveWaterData();

    // Trigger confetti if goal reached
    if (progress >= 100 && progress < 101) {
        triggerConfetti();
    }
}

// Add water
function addWater() {
    const amount = parseInt(waterAmount.value);
    waterData.history.push(waterData.current);
    waterData.current += amount;
    // Ensure current water does not exceed cup capacity
    if (waterData.current > CUP_CAPACITY_ML) {
        waterData.current = CUP_CAPACITY_ML;
    }
    updateWaterDisplay();
}

// Undo last water addition
function undoWater() {
    if (waterData.history.length > 0) {
        waterData.current = waterData.history.pop();
        updateWaterDisplay();
    }
}

// Reset water tracking
function resetWater() {
    if (confirm('Are you sure you want to reset your water intake for today?')) {
        waterData.current = 0;
        waterData.history = [];
        updateWaterDisplay();
    }
}

// Update goal
function updateGoal() {
    let goalLiters = parseFloat(waterGoal.value);
    CUP_CAPACITY_LITERS = goalLiters;
    CUP_CAPACITY_ML = CUP_CAPACITY_LITERS * 1000;
    waterData.goal = CUP_CAPACITY_ML;
    updateWaterDisplay();
}

// Toggle reminder settings
function toggleSettings() {
    reminderSettings.classList.toggle('hidden');
}

// Confetti animation
function triggerConfetti() {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        
        // Confetti from left
        confetti(Object.assign({}, defaults, { 
            particleCount, 
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } 
        }));
        
        // Confetti from right
        confetti(Object.assign({}, defaults, { 
            particleCount, 
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } 
        }));
    }, 250);
} 
// --- 3 Main Health Goals Interactivity ---
(function() {
  // Goal radio groups
  const emotionalRadios = document.querySelectorAll('input[name="emotional-goal"]');
  const physicalRadios = document.querySelectorAll('input[name="physical-goal"]');
  const studyRadios = document.querySelectorAll('input[name="study-goal"]');
  const successMsg = document.getElementById('goals-success-message');
  const confettiCanvas = document.getElementById('goals-confetti');
  let confettiActive = false;

  function checkAllSelected() {
    const emotional = Array.from(emotionalRadios).some(r => r.checked);
    const physical = Array.from(physicalRadios).some(r => r.checked);
    const study = Array.from(studyRadios).some(r => r.checked);
    return emotional && physical && study;
  }

  function showSuccess() {
    if (successMsg) successMsg.classList.remove('hidden');
    if (confettiCanvas && !confettiActive) {
      confettiActive = true;
      launchConfetti();
      setTimeout(() => {
        confettiActive = false;
        if (confettiCanvas) confettiCanvas.classList.add('hidden');
      }, 2000);
    }
  }

  function hideSuccess() {
    if (successMsg) successMsg.classList.add('hidden');
  }

  function launchConfetti() {
    if (!confettiCanvas) return;
    confettiCanvas.classList.remove('hidden');
    const ctx = confettiCanvas.getContext('2d');
    const W = confettiCanvas.width = confettiCanvas.offsetWidth;
    const H = confettiCanvas.height = confettiCanvas.offsetHeight;
    const colors = ['#A7C7E7', '#FFD6B0', '#B6E2A1', '#FFB3B3'];
    const confetti = Array.from({length: 30}, () => ({
      x: Math.random() * W,
      y: Math.random() * H * 0.5,
      r: Math.random() * 6 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      vy: Math.random() * 2 + 2,
      vx: (Math.random() - 0.5) * 2
    }));
    let frame = 0;
    function draw() {
      ctx.clearRect(0, 0, W, H);
      confetti.forEach(c => {
        ctx.beginPath();
        ctx.arc(c.x, c.y, c.r, 0, 2 * Math.PI);
        ctx.fillStyle = c.color;
        ctx.globalAlpha = 0.8;
        ctx.fill();
        c.y += c.vy;
        c.x += c.vx;
        if (c.y > H) c.y = -10;
        if (c.x < 0) c.x = W;
        if (c.x > W) c.x = 0;
      });
      ctx.globalAlpha = 1.0;
      frame++;
      if (frame < 60) requestAnimationFrame(draw);
      else confettiCanvas.classList.add('hidden');
    }
    draw();
  }

  function updateGoals() {
    if (checkAllSelected()) {
      showSuccess();
    } else {
      hideSuccess();
    }
  }

  emotionalRadios.forEach(r => r.addEventListener('change', updateGoals));
  physicalRadios.forEach(r => r.addEventListener('change', updateGoals));
  studyRadios.forEach(r => r.addEventListener('change', updateGoals));
})();

document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll(".goal-section");
  
    sections.forEach((section) => {
      const input = section.querySelector(".goal-input");
      const button = section.querySelector(".goal-submit");
      const list = section.querySelector(".goal-list");
      const inputArea = section.querySelector(".goal-input-area");
      const settingsBtn = section.querySelector(".goal-settings");
  
      const borderColor = section.dataset.color;
      const titleColor = section.dataset.headingColor;
      section.querySelector(".goal-title").style.color = titleColor;
  
      settingsBtn.addEventListener("click", () => {
        inputArea.classList.remove("hidden");
        settingsBtn.style.display = "none";
      });
  
      button.addEventListener("click", function () {
        const value = input.value.trim();
        if (!value) return;
  
        const label = document.createElement("label");
        label.style.borderColor = borderColor;
  
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
  
        const span = document.createElement("span");
        span.textContent = value;
  
        checkbox.addEventListener("change", () => {
          span.classList.toggle("completed", checkbox.checked);
        });
  
        label.appendChild(checkbox);
        label.appendChild(span);
        list.innerHTML = "";
        list.appendChild(label);
  
        input.value = "";
        inputArea.classList.add("hidden");
        settingsBtn.style.display = "inline-block";
      });
    });
  });
  
