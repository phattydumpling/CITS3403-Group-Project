// darkmode.js

document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    toggle.addEventListener('change', function () {
        document.body.classList.toggle('dark-mode');
    });

    // Calendar Setup
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
                // Example static events
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
});

// Task Management
const taskForm = document.getElementById('taskForm');
const taskInput = document.getElementById('taskInput');
const taskList = document.getElementById('taskList');

taskForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const taskText = taskInput.value.trim();
    if (taskText !== "") {
        const li = createTaskItem(taskText);
        taskList.appendChild(li);
        taskInput.value = '';
    }
});

function createTaskItem(text) {
    const li = document.createElement('li');
    li.className = 'list-group-item task-item';
    li.draggable = true;

    // Task left section: checkbox + text
    const taskLeft = document.createElement('div');
    taskLeft.className = 'task-left';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';

    const span = document.createElement('span');
    span.textContent = text;
    span.className = 'task-text';

    checkbox.addEventListener('change', () => {
        span.classList.toggle('completed', checkbox.checked);
    });

    taskLeft.appendChild(checkbox);
    taskLeft.appendChild(span);

    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.innerHTML = '&times;';
    deleteBtn.addEventListener('click', () => {
        li.remove();
    });

    li.appendChild(taskLeft);
    li.appendChild(deleteBtn);

    addDragEvents(li);
    return li;
}

// Drag and drop reordering
let draggedItem = null;

function addDragEvents(item) {
    item.addEventListener('dragstart', () => {
        draggedItem = item;
        setTimeout(() => item.classList.add('dragging'), 0);
    });

    item.addEventListener('dragend', () => {
        item.classList.remove('dragging');
        draggedItem = null;
    });

    item.addEventListener('dragover', (e) => e.preventDefault());

    item.addEventListener('drop', (e) => {
        e.preventDefault();
        if (draggedItem && draggedItem !== item) {
            const siblings = [...taskList.children];
            const draggedIndex = siblings.indexOf(draggedItem);
            const targetIndex = siblings.indexOf(item);
            if (draggedIndex < targetIndex) {
                taskList.insertBefore(draggedItem, item.nextSibling);
            } else {
                taskList.insertBefore(draggedItem, item);
            }
        }
    });
}