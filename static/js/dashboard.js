// =====================
// DARK MODE TOGGLE
// =====================
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.addEventListener('change', function () {
            document.body.classList.toggle('dark-mode');
        });
    }

    // =====================
    // FULLCALENDAR SETUP
    // =====================
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            height: 'auto',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek'
            },
            events: [
                {
                    title: 'Assignment Due',
                    start: new Date().toISOString().split('T')[0]
                },
                {
                    title: 'Group Study',
                    start: new Date(new Date().setDate(new Date().getDate() + 3)).toISOString().split('T')[0]
                }
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
    const taskList = document.getElementById('taskList');

    if (taskForm && taskInput && taskList && taskColor) {
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const taskText = taskInput.value.trim();
            const selectedColor = taskColor.value;
            if (taskText !== "") {
                const li = createTaskItem(taskText, selectedColor);
                taskList.appendChild(li);
                taskInput.value = '';
                taskColor.value = 'yellow'; // reset default
            }
        });
    }

    function createTaskItem(text, color = 'yellow') {
        const li = document.createElement('li');
        li.className = 'task-item';
        li.draggable = true;

        const dot = document.createElement('span');
        dot.className = `task-dot ${color}`;

        const span = document.createElement('span');
        span.textContent = text;

        li.appendChild(dot);
        li.appendChild(span);

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
