// =====================
// DARK MODE TOGGLE
// =====================
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    const dot = document.querySelector('.dot'); // the small circle

    if (toggle) {
        toggle.addEventListener('change', function () {
            document.body.classList.toggle('dark-mode');

            // Move the dot
            if (toggle.checked) {
                dot.classList.add('translate-x-4');
            } else {
                dot.classList.remove('translate-x-4');
            }
        });
    }

    // =====================
    // Navbar toggle for mobile
    // =====================
    document.getElementById('nav-toggle').addEventListener('click', function () {
        const navContent = document.getElementById('nav-content');
        navContent.classList.toggle('hidden');
    });

    // =====================
    // GLOBAL CALENDAR INSTANCE
    // =====================
    let calendar = null;

    // =====================
    // FULLCALENDAR SETUP
    // =====================
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            height: 'auto',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: [
            ]
        });
        calendar.render();
    }

    // =====================
    // TASK CREATION LOGIC
    // =====================
    const taskForm = document.getElementById('taskForm');
    const taskInput = document.getElementById('taskInput');
    const taskColor = document.getElementById('taskColor');
    const taskDueDate = document.getElementById('taskDueDate');
    const taskList = document.getElementById('taskList');

    if (taskForm && taskInput && taskColor && taskDueDate && taskList) {
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const taskText = taskInput.value.trim();
            const selectedColor = taskColor.value;
            const dueDate = taskDueDate.value;

            if (taskText && dueDate) {
                let calendarEvent = null;

                // ✅ Add to calendar ONCE here
                if (calendar) {
                    calendarEvent = calendar.addEvent({
                        title: taskText,
                        start: dueDate,
                        allDay: true
                    });
                }

                // Pass calendarEvent to the task element
                const li = createTaskItem(taskText, selectedColor, calendarEvent);
                taskList.appendChild(li);

                taskInput.value = '';
                taskColor.value = 'yellow';
                taskDueDate.value = '';
            }
        });
    }

    function createTaskItem(text, color = 'yellow', calendarEvent = null) {
        const li = document.createElement('li');
        li.className = 'task-item';
        li.draggable = true;

        const dot = document.createElement('span');
        dot.className = `task-dot ${color}`;

        const span = document.createElement('span');
        span.textContent = text;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn ms-auto';
        deleteBtn.innerHTML = '&times;';
        deleteBtn.title = 'Delete task';

        deleteBtn.addEventListener('click', () => {
            if (calendarEvent) {
                calendarEvent.remove(); // Remove from calendar
            }
            li.remove(); // Remove from list
        });

        li.appendChild(dot);
        li.appendChild(span);
        li.appendChild(deleteBtn);

        addDragEvents(li);
        return li;
    }



    // =====================
    // DRAG-AND-DROP SORTING
    // =====================
    let dragged = null;

    document.querySelectorAll('.sortable-list').forEach(list => {
        list.addEventListener('dragstart', e => {
            if (e.target.classList.contains('task-item')) {
                dragged = e.target;
                e.target.classList.add('dragging');
            }
        });

        list.addEventListener('dragend', e => {
            if (dragged) {
                dragged.classList.remove('dragging');
                dragged = null;
            }
        });

        list.addEventListener('dragover', e => {
            e.preventDefault();
            const afterElement = getDragAfterElement(list, e.clientY);
            if (dragged && afterElement == null) {
                list.appendChild(dragged);
            } else if (dragged && afterElement) {
                list.insertBefore(dragged, afterElement);
            }
        });
    });

    function addDragEvents(item) {
        item.addEventListener('dragstart', () => {
            dragged = item;
            setTimeout(() => item.classList.add('dragging'), 0);
        });

        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            dragged = null;
        });
    }

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.task-item:not(.dragging)')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // =====================
    // Initialize drag on any preloaded tasks
    // =====================
    document.querySelectorAll('#taskList .task-item').forEach(addDragEvents);
});
