// JavaScript for the Share Data page
function shareData() {
    const dataToShare = {
        study_progress: document.getElementById('shareStudyProgress').checked,
        mood: document.getElementById('shareMood').checked,
        tasks: document.getElementById('shareTasks').checked
    };

    // Get selected friends
    const selectedFriends = Array.from(document.querySelectorAll('.friend-checkbox:checked')).map(checkbox => checkbox.id.replace('friend_', ''));

    // Check if any data is selected
    if (!dataToShare.study_progress && !dataToShare.mood && !dataToShare.tasks) {
        showModal('No Data Selected', 'Please select at least one type of data to share.');
        return;
    }

    // Check if any friends are selected
    if (selectedFriends.length === 0) {
        showModal('No Friends Selected', 'Please select at least one friend to share with.');
        return;
    }

    // Share with each selected friend
    const sharePromises = selectedFriends.map(friendId => 
        fetch('/api/share_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                friend_id: friendId,
                data: dataToShare
            })
        }).then(response => response.json())
    );

    Promise.all(sharePromises)
        .then(results => {
            const allSuccessful = results.every(result => result.success);
            if (allSuccessful) {
                showModal('Success', 'Data shared successfully with all selected friends!');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showModal('Error', 'Error sharing data with some friends. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showModal('Error', 'Error sharing data. Please try again.');
        });
}

function showModal(title, message) {
    const modal = document.getElementById('customModal');
    const modalContent = document.getElementById('modalContent');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Trigger animation
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('customModal');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }, 200);
}

// Close modal when clicking outside
document.getElementById('customModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
}); 