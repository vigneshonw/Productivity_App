// Basic example: Confirm before marking a goal completed
document.addEventListener('DOMContentLoaded', function() {
    const completeLinks = document.querySelectorAll('a.complete-goal');

    completeLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            if (!confirm('Mark this goal as completed?')) {
                event.preventDefault();
            }
        });
    });
});
