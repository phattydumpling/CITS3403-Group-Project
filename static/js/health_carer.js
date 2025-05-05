// Global variables
let moodChart = null;

function deleteEntry(entryId) {
    if (!confirm('Are you sure you want to delete this entry?')) {
        return;
    }

    fetch(`/api/mood_entries/${entryId}`, {
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
        const entryElement = document.getElementById(`entry-${entryId}`);
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
        const sleepData = new Array(7).fill(null);
        
        entries.forEach(entry => {
            const date = new Date(entry.created_at);
            const dayIndex = date.getDay();
            moodData[dayIndex] = entry.mood_score;
            sleepData[dayIndex] = entry.sleep_quality;
        });

        moodChart.data.datasets[0].data = moodData;
        moodChart.data.datasets[1].data = sleepData;
        moodChart.update();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete entry. Please try again.');
    });
}

function addEntryToList(entry) {
    const entriesDiv = document.getElementById('recentEntries');
    const entryElement = document.createElement('div');
    entryElement.className = 'bg-gray-50 rounded-lg p-4';
    entryElement.id = `entry-${entry.id}`;
    entryElement.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm text-gray-500">${new Date(entry.created_at).toLocaleString()}</p>
                <p class="font-medium">Mood: ${entry.mood_score}/10</p>
                <p class="font-medium">Sleep: ${entry.sleep_quality}/10</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-gray-600">${entry.reflection}</p>
                <button onclick="deleteEntry(${entry.id})" 
                    class="mt-2 text-red-600 hover:text-red-800 text-sm font-medium">
                    Delete Entry
                </button>
            </div>
        </div>
    `;
    entriesDiv.insertBefore(entryElement, entriesDiv.firstChild);
}

document.addEventListener('DOMContentLoaded', function() {
    // Mood slider value display
    const moodSlider = document.getElementById('mood');
    const moodValue = document.getElementById('moodValue');
    const sleepSlider = document.getElementById('sleep');
    const sleepValue = document.getElementById('sleepValue');

    // Set initial values
    moodSlider.value = 5;
    moodValue.textContent = '5';
    sleepSlider.value = 5;
    sleepValue.textContent = '5';

    moodSlider.addEventListener('input', function() {
        moodValue.textContent = this.value;
    });

    sleepSlider.addEventListener('input', function() {
        sleepValue.textContent = this.value;
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
            }, {
                label: 'Sleep',
                data: [6, 7, 8, 6, 7, 8, 7],
                borderColor: '#10B981',
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
            sleep_quality: parseInt(sleepSlider.value),
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
            sleepSlider.value = 5;
            sleepValue.textContent = '5';
            document.getElementById('reflection').value = '';

            // Refresh chart data
            return fetch('/api/mood_entries');
        })
        .then(response => response.json())
        .then(entries => {
            // Update chart data
            const moodData = new Array(7).fill(null);
            const sleepData = new Array(7).fill(null);
            
            entries.forEach(entry => {
                const date = new Date(entry.created_at);
                const dayIndex = date.getDay();
                moodData[dayIndex] = entry.mood_score;
                sleepData[dayIndex] = entry.sleep_quality;
            });

            moodChart.data.datasets[0].data = moodData;
            moodChart.data.datasets[1].data = sleepData;
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
            const sleepData = new Array(7).fill(null);
            
            entries.forEach(entry => {
                const date = new Date(entry.created_at);
                const dayIndex = date.getDay();
                moodData[dayIndex] = entry.mood_score;
                sleepData[dayIndex] = entry.sleep_quality;
            });

            // Update chart data
            moodChart.data.datasets[0].data = moodData;
            moodChart.data.datasets[1].data = sleepData;
            moodChart.update();
        })
        .catch(error => console.error('Error loading mood entries:', error));
}); 