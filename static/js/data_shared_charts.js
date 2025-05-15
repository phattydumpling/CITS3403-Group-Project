// Global chart instances object
window.chartInstances = window.chartInstances || {};

// Common chart options
const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
            labels: {
                font: {
                    size: 12
                },
                color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
            }
        },
        title: {
            display: true,
            font: {
                size: 16,
                weight: 'bold'
            },
            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151',
            padding: 20
        }
    }
};

// Toggle functions
function toggleUserSection(userId) {
    const section = document.getElementById(userId);
    const icon = document.getElementById('icon-' + userId.replace('user-', ''));
    section.classList.toggle('hidden');
    icon.classList.toggle('rotate-180');
}

function toggleDataTypeSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById('icon-' + sectionId);
    section.classList.toggle('hidden');
    icon.classList.toggle('rotate-180');
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Study Progress Charts
    document.querySelectorAll('[id^="studyChart_"]').forEach(canvas => {
        const chartId = canvas.id;
        const dataId = chartId.split('_')[1];
        const studyData = JSON.parse(document.getElementById('studyData_' + dataId).textContent);
        
        if (window.chartInstances[chartId]) {
            window.chartInstances[chartId].destroy();
        }
        
        const studyCtx = canvas.getContext('2d');
        const studyLabels = studyData.map(session => session.subject);
        const studyDurations = studyData.map(session => {
            const start = new Date(session.start_time);
            const end = session.end_time ? new Date(session.end_time) : new Date();
            return (end - start) / (1000 * 60 * 60); // Convert to hours
        });

        window.chartInstances[chartId] = new Chart(studyCtx, {
            type: 'bar',
            data: {
                labels: studyLabels,
                datasets: [{
                    label: 'Study Duration (hours)',
                    data: studyDurations,
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 2,
                    borderRadius: 5,
                    barThickness: 30
                }]
            },
            options: {
                ...commonChartOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hours',
                            font: {
                                size: 12
                            },
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    });

    // Mood Charts
    document.querySelectorAll('[id^="moodChart_"]').forEach(canvas => {
        const chartId = canvas.id;
        const dataId = chartId.split('_')[1];
        const moodData = JSON.parse(document.getElementById('moodData_' + dataId).textContent);
        
        if (window.chartInstances[chartId]) {
            window.chartInstances[chartId].destroy();
        }
        
        const moodCtx = canvas.getContext('2d');
        const moodLabels = moodData.map(entry => new Date(entry.created_at).toLocaleDateString());
        const moodScores = moodData.map(entry => entry.mood_score);

        window.chartInstances[chartId] = new Chart(moodCtx, {
            type: 'line',
            data: {
                labels: moodLabels,
                datasets: [{
                    label: 'Mood Score',
                    data: moodScores,
                    borderColor: '#F97316', // Vibrant orange
                    backgroundColor: 'rgba(249, 115, 22, 0.15)', // Light orange with transparency
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#F97316', // Vibrant orange
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    borderWidth: 3
                }]
            },
            options: {
                ...commonChartOptions,
                scales: {
                    y: {
                        min: 0,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Mood Score',
                            font: {
                                size: 12
                            },
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    });

    // Tasks Charts
    document.querySelectorAll('[id^="tasksChart_"]').forEach(canvas => {
        const chartId = canvas.id;
        const dataId = chartId.split('_')[1];
        const tasksData = JSON.parse(document.getElementById('tasksData_' + dataId).textContent);
        
        if (window.chartInstances[chartId]) {
            window.chartInstances[chartId].destroy();
        }
        
        const tasksCtx = canvas.getContext('2d');
        const taskDates = tasksData.map(task => new Date(task.completed_at).toLocaleDateString());
        const taskCounts = {};
        taskDates.forEach(date => {
            taskCounts[date] = (taskCounts[date] || 0) + 1;
        });

        window.chartInstances[chartId] = new Chart(tasksCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(taskCounts),
                datasets: [{
                    label: 'Completed Tasks',
                    data: Object.values(taskCounts),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 2,
                    borderRadius: 5,
                    barThickness: 30
                }]
            },
            options: {
                ...commonChartOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Tasks',
                            font: {
                                size: 12
                            },
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    });
}); 