const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

document.addEventListener("DOMContentLoaded", function () {
    const calendarDiv = document.getElementById("flatCalendar");

    if (calendarDiv) {
        flatpickr(calendarDiv, {
            inline: true,
            defaultDate: new Date(),
            clickOpens: false,
            static: true,
            className: "w-full",
            monthSelectorType: "static",
            disableMobile: true
        });
    }
    
    // Donut chart for unit distribution
    async function updateDonutChart() {
        try {
            const response = await fetch('/api/unit_distribution');
            const data = await response.json();
            const donutChartEl = document.getElementById("donutChart");
            const existingChart = Chart.getChart(donutChartEl);
            
            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "70%",
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#6b7280',
                            padding: 10,
                            boxWidth: 12,
                            generateLabels: function(chart) {
                                // Only show subject name in legend
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        return {
                                            text: label,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                return `${label}: ${value} min`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Study Time per Unit (minutes)',
                        color: '#111827',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            };
            
            if (existingChart) {
                existingChart.data.labels = data.labels;
                existingChart.data.datasets[0].data = data.data;
                existingChart.options = chartOptions;
                existingChart.update();
            } else {
                new Chart(donutChartEl, {
                    type: "doughnut",
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.data,
                            backgroundColor: [
                                "#6366f1", // indigo
                                "#f59e0b", // amber
                                "#10b981", // emerald
                                "#ef4444",  // red
                                "#3b82f6", // blue
                                "#a21caf", // purple
                                "#f43f5e"  // pink
                            ]
                        }]
                    },
                    options: chartOptions
                });
            }
        } catch (error) {
            console.error('Error fetching unit distribution:', error);
        }
    }

    updateDonutChart();

    // Line chart for time studied
    const lineChartEl = document.getElementById("lineChart");
    const viewSelect = document.getElementById("timeViewSelect");

    if (lineChartEl && viewSelect) {
        let lineChart = Chart.getChart(lineChartEl);
        
        async function updateChart(view) {
            try {
                const response = await fetch(`/api/study_sessions?view=${view}`);
                const data = await response.json();
                const maxValue = Math.max(...data.data);
                let suggestedMax = 1;
                if (maxValue > 0) {
                    suggestedMax = Math.ceil(maxValue * 1.2 * 10) / 10; // 20% headroom
                }
                // Only show minutes for day view
                const showMinutes = view === 'day';
                
                const label = showMinutes ? 'Minutes Studied' : 'Hours Studied';
                // Calculate total based on view type
                const totalHours = data.data.reduce((a, b) => a + b, 0);
                const totalDisplay = showMinutes ? 
                    `${Math.round(totalHours)}m` : 
                    `${totalHours.toFixed(1)}h`;

                const chartConfig = {
                    type: "line",
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: label,
                            data: data.data,
                            borderColor: view === 'day' ? "#f59e0b" : view === 'week' ? "#3b82f6" : "#10b981",
                            backgroundColor: view === 'day' ? "rgba(245, 158, 11, 0.1)" : 
                                           view === 'week' ? "rgba(59, 130, 246, 0.1)" : 
                                           "rgba(16, 185, 129, 0.1)",
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: view === 'day' ? "#f59e0b" : 
                                                view === 'week' ? "#3b82f6" : 
                                                "#10b981",
                            pointBorderColor: "#ffffff",
                            pointBorderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            intersect: false,
                            mode: 'index'
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                suggestedMax: suggestedMax,
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)',
                                    drawBorder: false
                                },
                                ticks: {
                                    maxTicksLimit: 5,
                                    padding: 10,
                                    color: '#6b7280',
                                    font: {
                                        size: 12
                                    },
                                    callback: function(value) {
                                        if (showMinutes) {
                                            return Math.round(value) + 'm';
                                        }
                                        return value.toFixed(1) + 'h';
                                    }
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    padding: 10,
                                    color: '#6b7280',
                                    font: {
                                        size: 12
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                padding: 12,
                                titleFont: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                bodyFont: {
                                    size: 13
                                },
                                callbacks: {
                                    label: function(context) {
                                        const value = context.parsed.y;
                                        if (showMinutes) {
                                            return `${Math.round(value)}m`;
                                        }
                                        return `${value.toFixed(1)}h`;
                                    }
                                }
                            }
                        }
                    }
                };

                if (lineChart) {
                    lineChart.data = chartConfig.data;
                    lineChart.options = chartConfig.options;
                    lineChart.update();
                } else {
                    lineChart = new Chart(lineChartEl, chartConfig);
                }

                // Update the title in the HTML
                const titleElement = lineChartEl.closest('.bg-white').querySelector('h4');
                if (titleElement) {
                    titleElement.innerHTML = `Time Studied <span class="text-indigo-600 dark:text-indigo-300">(${totalDisplay})</span>`;
                }
            } catch (error) {
                console.error('Error fetching study session data:', error);
            }
        }

        // Initial chart load
        updateChart(viewSelect.value);

        // Handle dropdown change
        viewSelect.addEventListener("change", function() {
            updateChart(this.value);
        });
    }

    // Todo list functionality
    const taskForm = document.getElementById("taskForm");
    const taskInput = document.getElementById("taskInput");
    const taskList = document.getElementById("taskList");

    if (taskForm && taskInput && taskList) {
        // Load existing tasks
        loadTasks();

        taskForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = taskInput.value.trim();
            if (!text) return;

            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json','X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ title: text })
                });

                if (response.ok) {
                    const task = await response.json();
                    const li = createTaskItem(task);
                    taskList.insertBefore(li, taskList.firstChild);
                    taskInput.value = "";
                } else {
                    console.error('Failed to create task');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });

        async function loadTasks() {
            try {
                const response = await fetch('/api/tasks');
                if (response.ok) {
                    const tasks = await response.json();
                    taskList.innerHTML = '';
                    tasks.forEach(task => {
                        const li = createTaskItem(task);
                        taskList.appendChild(li);
                    });
                }
            } catch (error) {
                console.error('Error loading tasks:', error);
            }
        }

        async function deleteTask(taskId) {
            try {
                const response = await fetch(`/api/tasks/${taskId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });
                if (!response.ok) {
                    console.error('Failed to delete task');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }        

        let dragged = null;

        function addDragEvents(item) {
            item.addEventListener("dragstart", () => {
                dragged = item;
                item.classList.add("dragging");
            });

            item.addEventListener("dragend", () => {
                item.classList.remove("dragging");
                dragged = null;
            });

            item.addEventListener("dragover", (e) => e.preventDefault());

            item.addEventListener("drop", (e) => {
                e.preventDefault();
                if (dragged && dragged !== item) {
                    const items = [...taskList.children];
                    const dropIndex = items.indexOf(item);
                    const dragIndex = items.indexOf(dragged);
                    if (dragIndex < dropIndex) {
                        taskList.insertBefore(dragged, item.nextSibling);
                    } else {
                        taskList.insertBefore(dragged, item);
                    }
                }
            });
        }

        function createTaskItem(task) {
            const li = document.createElement("li");
            li.className = "flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-600 shadow-sm hover:shadow-md transition-shadow duration-200 group cursor-grab";
            li.draggable = true;
            li.dataset.taskId = task.id;

            // Check button
            const checkBtn = document.createElement("button");
            checkBtn.className = "w-6 h-6 flex items-center justify-center rounded-full border-2 border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700 mr-3 group-hover:border-indigo-500 transition-colors duration-200 focus:outline-none";
            checkBtn.innerHTML = '<svg class="w-4 h-4 text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity duration-200" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>';
            
            // Set initial state based on task status
            if (task.status === 'completed') {
                li.classList.add('todo-completed');
                checkBtn.classList.add('todo-check-checked');
                checkBtn.querySelector('svg').classList.remove('opacity-0');
            }

            // Add click handler for checkbox
            checkBtn.addEventListener('click', async function () {
                const isCompleted = li.classList.contains('todo-completed');
                try {
                    const response = await fetch(`/api/tasks/${task.id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            status: isCompleted ? 'pending' : 'completed'
                        })
                    });
                    
                    if (response.ok) {
                        li.classList.toggle('todo-completed');
                        checkBtn.classList.toggle('todo-check-checked');
                        span.classList.toggle('line-through');
                    } else {
                        console.error('Failed to update task status');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });

            // Task text
            const span = document.createElement("span");
            span.textContent = task.title;
            span.className = "flex-1 truncate text-gray-900 dark:text-white font-medium";
            if (task.status === 'completed') {
                span.classList.add('line-through');
            }

            // Delete button
            const del = document.createElement("button");
            del.innerHTML = '<i class="fas fa-trash"></i>';
            del.className = "ml-3 text-red-500 hover:text-red-700 bg-red-50 dark:bg-red-900 rounded-full p-1.5 transition-colors duration-200 focus:outline-none";
            del.title = "Delete task";
            del.onclick = async () => {
                await deleteTask(task.id);
                li.remove();
            };

            li.appendChild(checkBtn);
            li.appendChild(span);
            li.appendChild(del);

            addDragEvents(li);
            return li;
        }
    }

    function updateWeeklyMood() {
        fetch('/api/mood_entries')
            .then(response => response.json())
            .then(entries => {
                // Get entries from the last 7 days in AWST
                const sevenDaysAgo = new Date();
                sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                
                // Convert to AWST (UTC+8)
                const awstOffset = 8 * 60; // 8 hours in minutes
                const localOffset = sevenDaysAgo.getTimezoneOffset();
                sevenDaysAgo.setMinutes(sevenDaysAgo.getMinutes() + localOffset + awstOffset);
                
                const recentEntries = entries.filter(entry => {
                    const entryDate = new Date(entry.created_at);
                    // Convert entry date to AWST
                    const entryAwst = new Date(entryDate.getTime() + (entryDate.getTimezoneOffset() + awstOffset) * 60000);
                    return entryAwst >= sevenDaysAgo;
                });

                if (recentEntries.length === 0) {
                    document.getElementById('moodEmoji').textContent = '😐';
                    document.getElementById('moodScore').textContent = 'N/A';
                    document.getElementById('moodDateRange').textContent = 'No entries in the past week';
                    return;
                }

                // Calculate average mood score
                const totalScore = recentEntries.reduce((sum, entry) => sum + entry.mood_score, 0);
                const averageScore = Math.ceil(totalScore / recentEntries.length);

                // Update emoji and score based on average
                const moodEmoji = document.getElementById('moodEmoji');
                const moodScore = document.getElementById('moodScore');

                if (averageScore >= 8) {
                    moodEmoji.textContent = '😊';
                } else if (averageScore >= 4) {
                    moodEmoji.textContent = '😐';
                } else {
                    moodEmoji.textContent = '😢';
                }

                moodScore.textContent = averageScore;

                // Update date range display
                const now = new Date();
                const awstNow = new Date(now.getTime() + (now.getTimezoneOffset() + awstOffset) * 60000);
                const awstSevenDaysAgo = new Date(sevenDaysAgo.getTime());
                
                const formatDate = (date) => {
                    return date.toLocaleDateString('en-AU', {
                        day: 'numeric',
                        month: 'short',
                        timeZone: 'Australia/Perth'
                    });
                };

                document.getElementById('moodDateRange').textContent = 
                    `${formatDate(awstSevenDaysAgo)} - ${formatDate(awstNow)}`;
            })
            .catch(error => console.error('Error loading mood entries:', error));
    }

    // Call updateWeeklyMood when the page loads
    updateWeeklyMood();

    // Time Remaining Tracker
    function updateTimeRemaining() {
        const now = new Date();
        
        // Calculate week remaining
        const startOfWeek = new Date(now);
        startOfWeek.setDate(now.getDate() - now.getDay());
        startOfWeek.setHours(0, 0, 0, 0);
        
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        endOfWeek.setHours(23, 59, 59, 999);
        
        const weekTotal = endOfWeek - startOfWeek;
        const weekRemaining = endOfWeek - now;
        const weekProgress = ((weekTotal - weekRemaining) / weekTotal) * 100;
        
        const weekDays = Math.floor(weekRemaining / (1000 * 60 * 60 * 24));
        const weekHours = Math.floor((weekRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        document.getElementById('weekRemaining').textContent = `${weekDays}d ${weekHours}h`;
        document.getElementById('weekProgress').style.width = `${weekProgress}%`;
        
        // Calculate month remaining
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);
        
        const monthTotal = endOfMonth - startOfMonth;
        const monthRemaining = endOfMonth - now;
        const monthProgress = ((monthTotal - monthRemaining) / monthTotal) * 100;
        
        const monthDays = Math.floor(monthRemaining / (1000 * 60 * 60 * 24));
        document.getElementById('monthRemaining').textContent = `${monthDays} days`;
        document.getElementById('monthProgress').style.width = `${monthProgress}%`;
        
        // Calculate year remaining
        const startOfYear = new Date(now.getFullYear(), 0, 1);
        const endOfYear = new Date(now.getFullYear(), 11, 31, 23, 59, 59, 999);
        
        const yearTotal = endOfYear - startOfYear;
        const yearRemaining = endOfYear - now;
        const yearProgress = ((yearTotal - yearRemaining) / yearTotal) * 100;
        
        const yearDays = Math.floor(yearRemaining / (1000 * 60 * 60 * 24));
        document.getElementById('yearRemaining').textContent = `${yearDays} days`;
        document.getElementById('yearProgress').style.width = `${yearProgress}%`;
    }

    // Update time remaining every minute
    updateTimeRemaining();
    setInterval(updateTimeRemaining, 60000);
});