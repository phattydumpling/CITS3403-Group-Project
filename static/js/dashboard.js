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
                // Only show minutes for day/week views with small values, always show hours for month
                const showMinutes = (view !== 'month') && (maxValue < 1);
                
                const label = (view === 'month') ? 'Hours Studied' : 'Minutes Studied';
                const chartConfig = {
                    type: "line",
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: label,
                            data: data.data,
                            borderColor: view === 'day' ? "#f59e0b" : view === 'week' ? "#3b82f6" : "#10b981",
                            fill: false,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                suggestedMax: suggestedMax,
                                ticks: {
                                    maxTicksLimit: 5,
                                    callback: function(value) {
                                        if (showMinutes) {
                                            return (value * 60).toFixed(0) + 'm';
                                        }
                                        return value.toFixed(1) + 'h';
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
                        'Content-Type': 'application/json',
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
                    method: 'DELETE'
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
            li.className = "flex items-center justify-between p-2 border rounded dark:bg-gray-700 dark:text-white bg-gray-50 cursor-grab";
            li.draggable = true;
            li.dataset.taskId = task.id;

            const span = document.createElement("span");
            span.textContent = task.title;

            const del = document.createElement("button");
            del.innerHTML = "&times;";
            del.className = "text-red-500 hover:text-red-700 text-lg font-bold ml-4 focus:outline-none";
            del.onclick = async () => {
                await deleteTask(task.id);
                li.remove();
            };

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
