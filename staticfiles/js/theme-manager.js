// Theme Management System
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.themeToggle = null;
        this.themeIcon = null;
        this.themeText = null;
        this.body = document.body;
        
        this.init();
    }

    init() {
        // Set initial theme
        this.body.setAttribute('data-theme', this.currentTheme);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }

    setupElements() {
        this.themeToggle = document.getElementById('toggle-theme');
        this.themeIcon = document.getElementById('theme-icon');
        this.themeText = document.getElementById('theme-text');

        console.log('Theme elements found:', {
            toggle: !!this.themeToggle,
            icon: !!this.themeIcon,
            text: !!this.themeText
        });

        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', (e) => this.toggleTheme(e));
            console.log('Theme toggle event listener added');
        }

        // Also setup mobile theme toggle if present
        const mobileToggle = document.getElementById('toggle-theme-mobile');
        const mobileIcon = document.getElementById('theme-icon-mobile');
        
        if (mobileToggle) {
            mobileToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme(e);
                if (mobileIcon) {
                    mobileIcon.className = this.currentTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
                }
            });
            console.log('Mobile theme toggle event listener added');
        }

        this.updateThemeUI();
    }

    toggleTheme(e) {
        if (e) e.preventDefault();
        
        console.log('toggleTheme called, current theme:', this.currentTheme);
        
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.body.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        
        console.log('Theme changed to:', this.currentTheme);
        
        this.updateThemeUI();
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: this.currentTheme } 
        }));
    }

    updateThemeUI() {
        console.log('Updating theme UI for theme:', this.currentTheme);
        
        if (this.themeIcon && this.themeText) {
            if (this.currentTheme === 'dark') {
                this.themeIcon.className = 'bi bi-sun-fill';
                this.themeText.textContent = 'Aydınlık Tema';
            } else {
                this.themeIcon.className = 'bi bi-moon-fill';
                this.themeText.textContent = 'Karanlık Tema';
            }
        } else if (this.themeIcon) {
            // For pages with only icon
            this.themeIcon.className = this.currentTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }

        // Update mobile icon if present
        const mobileIcon = document.getElementById('theme-icon-mobile');
        if (mobileIcon) {
            mobileIcon.className = this.currentTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        }

        console.log('Theme UI updated');
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (theme === 'dark' || theme === 'light') {
            this.currentTheme = theme;
            this.body.setAttribute('data-theme', this.currentTheme);
            localStorage.setItem('theme', this.currentTheme);
            this.updateThemeUI();
        }
    }
}

// Sidebar Management System  
class SidebarManager {
    constructor() {
        this.sidebar = null;
        this.sidebarToggle = null;
        this.mobileSidebarToggle = null;
        this.sidebarOverlay = null;
        this.mainContent = null;
        this.isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }

    setupElements() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
        this.sidebarOverlay = document.getElementById('sidebar-overlay');
        this.mainContent = document.getElementById('main-content');

        if (this.sidebar && this.isCollapsed) {
            this.sidebar.classList.add('collapsed');
            if (this.mainContent) {
                this.mainContent.classList.add('sidebar-collapsed');
            }
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Desktop sidebar toggle
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Mobile sidebar toggle
        if (this.mobileSidebarToggle) {
            this.mobileSidebarToggle.addEventListener('click', () => this.openMobileSidebar());
        }

        // Close mobile sidebar
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => this.closeMobileSidebar());
        }

        // Auto-close mobile sidebar on window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                this.closeMobileSidebar();
            }
        });
    }

    toggleSidebar() {
        if (!this.sidebar || !this.mainContent) return;

        this.sidebar.classList.toggle('collapsed');
        this.mainContent.classList.toggle('sidebar-collapsed');
        
        this.isCollapsed = this.sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', this.isCollapsed);
    }

    openMobileSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;

        this.sidebar.classList.add('mobile-open');
        this.sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeMobileSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;

        this.sidebar.classList.remove('mobile-open');
        this.sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Initialize managers
const themeManager = new ThemeManager();
const sidebarManager = new SidebarManager();

// Make managers globally available
window.themeManager = themeManager;
window.sidebarManager = sidebarManager;

// Utility functions for backward compatibility
window.toggleTheme = () => themeManager.toggleTheme();
window.getCurrentTheme = () => themeManager.getCurrentTheme();
window.setTheme = (theme) => themeManager.setTheme(theme);

// Debug logging
console.log('Theme Manager initialized with theme:', themeManager.getCurrentTheme());

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeManager, SidebarManager };
}