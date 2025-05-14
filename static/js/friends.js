// Modal logic for removing a friend
function showRemoveFriendModal(username, friendId) {
    document.getElementById('friendName').textContent = username;
    document.getElementById('removeFriendForm').action = `/remove_friend/${friendId}`;
    const modal = document.getElementById('removeFriendModal');
    const modalContent = document.getElementById('modalContent');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
    // Enable Enter key for confirm
    enterListener = enableEnterToConfirm(modal, document.querySelector('#removeFriendForm button[type="submit"]'));
}

function hideRemoveFriendModal() {
    const modal = document.getElementById('removeFriendModal');
    const modalContent = document.getElementById('modalContent');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
    // Remove Enter key listener
    if (enterListener) {
        disableEnterToConfirm(enterListener);
        enterListener = null;
    }
}

// Reusable Enter-to-confirm logic
let enterListener = null;
function enableEnterToConfirm(modalElement, confirmBtn) {
    function handler(e) {
        if (modalElement.classList.contains('flex') && (e.key === 'Enter' || e.keyCode === 13)) {
            e.preventDefault();
            confirmBtn.click();
        }
    }
    document.addEventListener('keydown', handler);
    return handler;
}
function disableEnterToConfirm(handler) {
    document.removeEventListener('keydown', handler);
} 