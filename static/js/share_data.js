// JavaScript for the Share Data page
async function shareData() {
    const dataToShare = {
        study_progress: document.getElementById('shareStudyProgress').checked,
        mood: document.getElementById('shareMood').checked,
        tasks: document.getElementById('shareTasks').checked
    };

    // Get selected friends
    const selectedFriends = Array.from(document.querySelectorAll('.friend-checkbox:checked')).map(cb => cb.id.replace('friend_', ''));

    // Validate selections
    if (!Object.values(dataToShare).some(v => v)) {
        showModal('Error', 'Please select at least one type of data to share.');
        return;
    }

    if (selectedFriends.length === 0) {
        showModal('Error', 'Please select at least one friend to share with.');
        return;
    }

    // Disable share button and show loading state
    const shareButton = document.querySelector('button[onclick="shareData()"]');
    const originalButtonText = shareButton.innerHTML;
    shareButton.disabled = true;
    shareButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sharing...';

    try {
        // Share with each selected friend
        const sharePromises = selectedFriends.map(async (friendId) => {
            const response = await fetch('/api/share_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    friend_id: friendId,
                    data: dataToShare
                })
            });

            const result = await response.json();
            
            if (!response.ok) {
                if (response.status === 429) {
                    // Rate limit error - show countdown
                    const errorMessage = result.error;
                    showModal('Rate Limited', errorMessage);
                    
                    // Start countdown timer
                    let timeLeft = 60; // 1 minute in seconds
                    const countdownInterval = setInterval(() => {
                        timeLeft--;
                        if (timeLeft <= 0) {
                            clearInterval(countdownInterval);
                            shareButton.disabled = false;
                            shareButton.innerHTML = originalButtonText;
                        } else {
                            shareButton.innerHTML = `<i class="fas fa-clock mr-2"></i>Wait ${timeLeft}s`;
                        }
                    }, 1000);
                    
                    throw new Error(errorMessage);
                }
                throw new Error(result.error || 'Failed to share data');
            }
            
            return result;
        });

        await Promise.all(sharePromises);
        showModal('Success', 'Data shared successfully!');
    } catch (error) {
        if (!error.message.includes('Rate Limited')) {
            showModal('Error', error.message);
        }
    } finally {
        // Only re-enable the button if we're not in a countdown
        if (!shareButton.innerHTML.includes('Wait')) {
            shareButton.disabled = false;
            shareButton.innerHTML = originalButtonText;
        }
    }
}

function showModal(title, message) {
    const modal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalContent = document.getElementById('modalContent');

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