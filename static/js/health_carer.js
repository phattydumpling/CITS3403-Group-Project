// Global variables
let moodChart = null;
let pendingDeleteId = null;

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
                    <p class="text-sm text-gray-500 dark:text-gray-400">${new Date(entry.created_at).toLocaleString()}</p>
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

        fetch('/api/mood_entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(entry => {
            // Add to recent entries
            addEntryToList(entry);
            
            // Reset form values
            moodSlider.value = 5;
            moodValue.textContent = '5';
            document.getElementById('reflection').value = '';

            // Refresh chart data
            return fetch('/api/mood_entries');
        })
        .then(response => response.json())
        .then(entries => {
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
    if (!dataToShare.study_progress && !dataToShare.mood && !dataToShare.tasks) {
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