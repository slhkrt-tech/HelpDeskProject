document.addEventListener('DOMContentLoaded', function () {
    
    // Collapsible textarea
    
    document.querySelectorAll('.textarea-container').forEach(container => {
        const textarea = container.querySelector('.collapsible-textarea');
        const toggle = container.querySelector('.toggle-arrow');

        // Başlangıç durumu

        textarea.classList.add('collapsed');
        textarea.style.height = '80px';
        toggle.innerHTML = '▼';

        toggle.addEventListener('click', () => {
            if (textarea.classList.contains('collapsed')) {
                textarea.style.height = '300px';
                textarea.classList.remove('collapsed');
                textarea.classList.add('expanded');
                toggle.innerHTML = '▲';
            } else {
                textarea.style.height = '80px';
                textarea.classList.remove('expanded');
                textarea.classList.add('collapsed');
                toggle.innerHTML = '▼';
            }
        });
    });

    // Modal

    const modal = document.getElementById('popupModal');
    const iframe = document.getElementById('modalIframe');
    const closeBtn = document.getElementById('closeModal');

    window.openModal = function(url) {
        iframe.src = url;
        modal.classList.add('show');
    };

    closeBtn.addEventListener('click', function() {
        modal.classList.remove('show');
        iframe.src = '';
    });
});