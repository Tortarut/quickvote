document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type="range"]').forEach(range => {
        const label = range.parentElement.querySelector('.rating-value');
        if (label) {
            range.addEventListener('input', () => {
                label.textContent = range.value;
            });
        }
    });
});

