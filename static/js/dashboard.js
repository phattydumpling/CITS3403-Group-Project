document.addEventListener("DOMContentLoaded", function () {
    const calendarDiv = document.getElementById("flatCalendar");

    if (calendarDiv) {
        flatpickr(calendarDiv, {
            inline: true,
            defaultDate: new Date(),
            clickOpens: false
        });
    }
    
    // Hardcoded data for the pie chart for units studied
    new Chart(document.getElementById("donutChart"), {
        type: "doughnut",
        data: {
            labels: ["CITS3403", "CITS3002", "CITS2007", "CITS2401"],
            datasets: [{
                data: [30, 25, 20, 25],
                backgroundColor: [
                    "#6366f1", // indigo
                    "#f59e0b", // amber
                    "#10b981", // emerald
                    "#ef4444"  // red
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#6b7280', // text-gray-500
                        padding: 10,
                        boxWidth: 12
                    }
                }
            }
        }
    });

    // Hardcoded data for the line chart for time studied
    const lineChartEl = document.getElementById("lineChart");
    const viewSelect = document.getElementById("timeViewSelect");

    if (lineChartEl && viewSelect) {
        const ctx = lineChartEl.getContext("2d");

        const dailyData = {
            labels: ["12AM", "4AM", "8AM", "12PM", "4PM", "8PM", "12AM"],
            datasets: [{
                label: "Hours Studied",
                data: [0, 0.5, 1.5, 2, 1, 0, 4],
                borderColor: "#f59e0b", // amber
                fill: false,
                tension: 0.4
            }]
        };

        const weeklyData = {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [{
                label: "Hours Studied",
                data: [2, 3, 1.5, 2.5, 3, 0, 1],
                borderColor: "#3b82f6", // blue
                fill: false,
                tension: 0.4
            }]
        };

        const monthlyData = {
            labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
            datasets: [{
                label: "Hours Studied",
                data: [8, 12, 9, 15],
                borderColor: "#10b981", // green
                fill: false,
                tension: 0.4
            }]
        };

        const chartConfig = {
            type: "line",
            data: weeklyData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        const lineChart = new Chart(ctx, chartConfig);

        // Handle dropdown change
        viewSelect.addEventListener("change", function () {
            const selected = viewSelect.value;
            if (selected === "day") {
                lineChart.data = dailyData;
            } else if (selected === "month") {
                lineChart.data = monthlyData;
            } else {
                lineChart.data = weeklyData;
            }
            lineChart.update();
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
                // Get entries from the last 7 days
                const sevenDaysAgo = new Date();
                sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                
                const recentEntries = entries.filter(entry => {
                    const entryDate = new Date(entry.created_at);
                    return entryDate >= sevenDaysAgo;
                });

                if (recentEntries.length === 0) {
                    document.getElementById('moodEmoji').textContent = '😐';
                    document.getElementById('moodScore').textContent = 'N/A';
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
            })
            .catch(error => console.error('Error loading mood entries:', error));
    }

    // Call updateWeeklyMood when the page loads
    updateWeeklyMood();
});
