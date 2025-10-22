// Modern Ticket List JavaScript
// ================================================================================

class TicketStatusManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeTooltips();
    }

    bindEvents() {
        // Durum değiştirme butonları
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('status-dropdown-item')) {
                this.handleStatusChange(e);
            }
        });

        // Dropdown toggle
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('status-change-dropdown')) {
                this.toggleDropdown(e);
            } else {
                this.closeAllDropdowns();
            }
        });

        // ESC tuşu ile dropdown kapat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    }

    async handleStatusChange(event) {
        event.preventDefault();
        
        const button = event.target;
        const ticketId = button.dataset.ticketId;
        const newStatus = button.dataset.status;
        const statusDisplay = button.textContent.trim();

        // Onay dialog
        const confirmed = await this.showConfirmDialog(
            `Talep #${ticketId} durumunu "${statusDisplay}" olarak değiştirmek istediğinizden emin misiniz?`
        );

        if (!confirmed) return;

        // Loading başlat
        this.showLoading();

        try {
            const response = await fetch(`/tickets/${ticketId}/change-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `status=${newStatus}`
            });

            const data = await response.json();

            if (data.success) {
                this.updateStatusUI(ticketId, newStatus, data.new_status_display || statusDisplay);
                this.showToast('Durum başarıyla güncellendi!', 'success');
                
                // Dropdown'ı güncelle
                this.updateDropdownOptions(ticketId, newStatus);
            } else {
                this.showToast(data.error || 'Durum güncellenirken bir hata oluştu.', 'error');
            }
        } catch (error) {
            console.error('Status change error:', error);
            this.showToast('Bağlantı hatası oluştu.', 'error');
        } finally {
            this.hideLoading();
            this.closeAllDropdowns();
        }
    }

    updateStatusUI(ticketId, newStatus, statusDisplay) {
        const statusBadge = document.getElementById(`status-badge-${ticketId}`);
        if (statusBadge) {
            // Eski class'ları temizle
            statusBadge.className = 'status-badge';
            
            // Yeni status class'ını ekle
            statusBadge.classList.add(`status-${newStatus}`);
            statusBadge.textContent = statusDisplay;

            // Animasyon efekti
            statusBadge.style.transform = 'scale(1.1)';
            setTimeout(() => {
                statusBadge.style.transform = 'scale(1)';
            }, 200);
        }
    }

    updateDropdownOptions(ticketId, currentStatus) {
        const dropdown = document.querySelector(`[data-ticket-id="${ticketId}"]`).closest('.status-action-container');
        const dropdownItems = dropdown.querySelectorAll('.status-dropdown-item');
        
        dropdownItems.forEach(item => {
            const itemStatus = item.dataset.status;
            // Mevcut durumu gizle, diğerlerini göster
            item.style.display = itemStatus === currentStatus ? 'none' : 'flex';
        });
    }

    toggleDropdown(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const button = event.target;
        const container = button.closest('.status-action-container');
        const dropdown = container.querySelector('.status-dropdown-menu');
        
        // Diğer dropdown'ları kapat
        this.closeAllDropdowns(container);
        
        // Bu dropdown'ı aç/kapat
        const isOpen = dropdown.style.display === 'block';
        dropdown.style.display = isOpen ? 'none' : 'block';
        
        if (!isOpen) {
            // Pozisyon ayarla
            this.positionDropdown(button, dropdown);
        }
    }

    positionDropdown(button, dropdown) {
        const buttonRect = button.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        
        // Eğer dropdown aşağı sığmıyorsa yukarı aç
        if (buttonRect.bottom + dropdownRect.height > viewportHeight) {
            dropdown.style.bottom = '100%';
            dropdown.style.top = 'auto';
            dropdown.style.marginBottom = '0.5rem';
            dropdown.style.marginTop = '0';
        } else {
            dropdown.style.top = '100%';
            dropdown.style.bottom = 'auto';
            dropdown.style.marginTop = '0.5rem';
            dropdown.style.marginBottom = '0';
        }
    }

    closeAllDropdowns(except = null) {
        const dropdowns = document.querySelectorAll('.status-dropdown-menu');
        dropdowns.forEach(dropdown => {
            if (except && except.contains(dropdown)) return;
            dropdown.style.display = 'none';
        });
    }

    showConfirmDialog(message) {
        return new Promise((resolve) => {
            // Modern confirmation dialog
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.style.background = 'rgba(0, 0, 0, 0.7)';
            
            const dialog = document.createElement('div');
            dialog.className = 'loading-spinner';
            dialog.style.maxWidth = '400px';
            dialog.innerHTML = `
                <div class="mb-3">
                    <i class="bi bi-question-circle text-warning" style="font-size: 2rem;"></i>
                </div>
                <h5 class="mb-3">Onay</h5>
                <p class="mb-4">${message}</p>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-secondary px-4" id="cancel-btn">İptal</button>
                    <button class="btn btn-primary px-4" id="confirm-btn">Evet</button>
                </div>
            `;
            
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
            
            // Event listeners
            const confirmBtn = dialog.querySelector('#confirm-btn');
            const cancelBtn = dialog.querySelector('#cancel-btn');
            
            confirmBtn.addEventListener('click', () => {
                document.body.removeChild(overlay);
                resolve(true);
            });
            
            cancelBtn.addEventListener('click', () => {
                document.body.removeChild(overlay);
                resolve(false);
            });
            
            // ESC tuşu
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    document.body.removeChild(overlay);
                    document.removeEventListener('keydown', escapeHandler);
                    resolve(false);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
            // Focus
            confirmBtn.focus();
        });
    }

    showLoading() {
        const overlay = document.createElement('div');
        overlay.id = 'status-loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
                <h6>Durum güncelleniyor...</h6>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('status-loading-overlay');
        if (overlay) {
            document.body.removeChild(overlay);
        }
    }

    showToast(message, type = 'info') {
        // Mevcut toast'ları temizle
        const existingToasts = document.querySelectorAll('.modern-toast');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `modern-toast ${type}`;
        
        const icon = type === 'success' ? 'check-circle-fill' : 
                    type === 'error' ? 'exclamation-triangle-fill' : 
                    'info-circle-fill';
        
        const iconColor = type === 'success' ? '#10b981' : 
                         type === 'error' ? '#ef4444' : 
                         '#3b82f6';
        
        toast.innerHTML = `
            <i class="bi bi-${icon}" style="color: ${iconColor}; font-size: 1.25rem;"></i>
            <span>${message}</span>
            <button type="button" style="background: none; border: none; color: #6b7280; font-size: 1.25rem; margin-left: auto;" onclick="this.parentElement.remove()">×</button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    getCSRFToken() {
        // Önce form input'undan al
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input && input.value) {
            return input.value;
        }
        
        // Sonra meta tag'den al
        const meta = document.querySelector('meta[name=csrf-token]');
        if (meta && meta.content) {
            return meta.content;
        }
        
        // Son olarak cookie'den al
        return this.getCookie('csrftoken') || '';
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    initializeTooltips() {
        // Bootstrap tooltip'leri başlat
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// CSS animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TicketStatusManager();
});

// Global functions for compatibility
window.TicketStatusManager = TicketStatusManager;