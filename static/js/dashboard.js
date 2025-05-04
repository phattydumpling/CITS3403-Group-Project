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
        taskForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const text = taskInput.value.trim();
            if (!text) return;
            const li = createTaskItem(text);
            taskList.appendChild(li);
            taskInput.value = "";
        });

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

        function createTaskItem(text) {
            const li = document.createElement("li");
            li.className = "flex items-center justify-between p-2 border rounded dark:bg-gray-700 dark:text-white bg-gray-50 cursor-grab";
            li.draggable = true;

            const span = document.createElement("span");
            span.textContent = text;

            const del = document.createElement("button");
            del.innerHTML = "&times;";
            del.className = "text-red-500 hover:text-red-700 text-lg font-bold ml-4 focus:outline-none";
            del.onclick = () => li.remove();

            li.appendChild(span);
            li.appendChild(del);

            addDragEvents(li);
            return li;
        }
    }
});
