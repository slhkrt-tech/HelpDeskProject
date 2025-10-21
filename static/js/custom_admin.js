document.addEventListener('DOMContentLoaded', function () {
    // -----------------------------------------------------------------
    // Collapsible textarea
    // -----------------------------------------------------------------
    
    setTimeout(function() {
        const textareas = document.querySelectorAll('.collapsible-textarea');
        textareas.forEach(textarea => {
            const toggle = document.createElement('span');
            toggle.innerHTML = '▼';
            toggle.className = 'toggle-arrow';
            textarea.parentNode.insertBefore(toggle, textarea.nextSibling);
            textarea.classList.add('collapsed');

            toggle.addEventListener('click', () => {
                if (textarea.classList.contains('collapsed')) {
                    textarea.style.height = '300px';
                    textarea.classList.remove('collapsed');
                    textarea.classList.add('expanded');
                } else {
                    textarea.style.height = '80px';
                    textarea.classList.remove('expanded');
                    textarea.classList.add('collapsed');
                }
            });
        });
    }, 500); // Admin sayfasında render gecikmesine karşı

    // -----------------------------------------------------------------
    // Modal container ekleme
    // -----------------------------------------------------------------

    let modal = document.createElement('div');
    modal.id = 'popupModal';
    modal.style.display = 'none';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.zIndex = '10000';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.innerHTML = `
        <div style="background:white; width:80%; height:80%; position:relative; padding:10px; box-shadow:0 0 10px #000;">
            <button id="closeModal" style="position:absolute; top:5px; right:10px; font-size:16px;">✖</button>
            <iframe id="modalIframe" src="" style="width:100%; height:100%; border:none;"></iframe>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('closeModal').onclick = function() {
        modal.style.display = 'none';
        document.getElementById('modalIframe').src = '';
    };

    // -----------------------------------------------------------------
    // Modal açma fonksiyonu
    // -----------------------------------------------------------------

    window.openModal = function(url) {
        document.getElementById('modalIframe').src = url;
        modal.style.display = 'flex';
    };
});