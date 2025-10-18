// theme-toggle.js

document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById('toggle-theme');
    const body = document.body;

    // Kaydedilmiş tema varsa uygula, yoksa dark mode
    
    const savedTheme = localStorage.getItem('theme') || 'dark';
    body.setAttribute('data-theme', savedTheme);

    // Toggle butonuna tıklandığında tema değiştir

    toggle.addEventListener('click', () => {
        const current = body.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        body.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
});