// Modern Ticket List JavaScript - Modal Version
document.addEventListener('DOMContentLoaded', function() {

    
    // Modal elements
    const statusModal = document.getElementById('statusChangeModal');
    const modalTitle = document.getElementById('modalTicketTitle');
    const modalCurrentStatus = document.getElementById('modalCurrentStatus');
    const newStatusSelect = document.getElementById('newStatusSelect');
    const confirmButton = document.getElementById('confirmStatusChange');
    
    let currentTicketId = null;
    let currentTicketStatus = null;
    
    // Status display names mapping
    const statusDisplayNames = {
        'open': 'Açık',
        'in_progress': 'İşlemde',
        'resolved': 'Çözümlendi',
        'closed': 'Kapalı'
    };
    
    // Bootstrap modal instance
    let modalInstance = null;
    
    // Initialize modal
    if (statusModal) {
        modalInstance = new bootstrap.Modal(statusModal);
        
        // Modal show event
        statusModal.addEventListener('show.bs.modal', function(event) {

            updateModalContent();
        });
        
        // Modal hide event
        statusModal.addEventListener('hide.bs.modal', function(event) {
            resetModal();
        });
    }
    
    // Event delegation for status change buttons
    document.addEventListener('click', function(event) {
        if (event.target.closest('.status-change-btn')) {
            const button = event.target.closest('.status-change-btn');
            handleStatusChangeClick(button);
        }
    });
    
    // New status select change event
    if (newStatusSelect) {
        newStatusSelect.addEventListener('change', function() {
            const selectedValue = this.value;
            const isValid = selectedValue && selectedValue !== currentTicketStatus;
            
            if (confirmButton) {
                confirmButton.disabled = !isValid;
            }
            

        });
    }
    
    // Confirm button click
    if (confirmButton) {
        confirmButton.addEventListener('click', function() {
            const newStatus = newStatusSelect.value;
            if (newStatus && currentTicketId) {
                changeTicketStatus(currentTicketId, newStatus);
            }
        });
    }
    
    function handleStatusChangeClick(button) {
        try {
            currentTicketId = button.dataset.ticketId;
            currentTicketStatus = button.dataset.currentStatus;
            const ticketTitle = button.dataset.ticketTitle;
            
            console.log('Opening status change modal:', {
                ticketId: currentTicketId,
                currentStatus: currentTicketStatus,
                title: ticketTitle
            });
            
            if (modalInstance) {
                modalInstance.show();
            }
        } catch (error) {

            showToast('Bir hata oluştu: ' + error.message, 'error');
        }
    }
    
    function updateModalContent() {
        if (!currentTicketId || !currentTicketStatus) return;
        
        // Update ticket title
        if (modalTitle) {
            const button = document.querySelector(`[data-ticket-id="${currentTicketId}"]`);
            const title = button ? button.dataset.ticketTitle : `Talep #${currentTicketId}`;
            modalTitle.textContent = title;
        }
        
        // Update current status display
        if (modalCurrentStatus) {
            const statusDisplay = statusDisplayNames[currentTicketStatus] || currentTicketStatus;
            modalCurrentStatus.textContent = statusDisplay;
            modalCurrentStatus.className = `current-status-display status-${currentTicketStatus}`;
        }
        
        // Reset and populate new status select
        if (newStatusSelect) {
            newStatusSelect.value = '';
            
            // Hide current status option
            Array.from(newStatusSelect.options).forEach(option => {
                if (option.value === currentTicketStatus) {
                    option.style.display = 'none';
                } else {
                    option.style.display = 'block';
                }
            });
        }
        
        // Disable confirm button initially
        if (confirmButton) {
            confirmButton.disabled = true;
        }
    }
    
    function resetModal() {
        currentTicketId = null;
        currentTicketStatus = null;
        
        if (modalTitle) modalTitle.textContent = '';
        if (modalCurrentStatus) {
            modalCurrentStatus.textContent = '';
            modalCurrentStatus.className = 'current-status-display';
        }
        if (newStatusSelect) newStatusSelect.value = '';
        if (confirmButton) confirmButton.disabled = true;
        

    }
    
    async function changeTicketStatus(ticketId, newStatus) {
        if (!ticketId || !newStatus) {

            return;
        }
        

        
        // Show loading state
        showLoadingOverlay('Durum değiştiriliyor...');
        
        try {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(`/tickets/${ticketId}/change-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    status: newStatus
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {

                
                // Update the status badge in the table
                updateStatusBadge(ticketId, newStatus, result.status_display);
                
                // Close modal
                if (modalInstance) {
                    modalInstance.hide();
                }
                
                // Show success message
                showToast(result.message || 'Durum başarıyla değiştirildi!', 'success');
                
            } else {

                showToast(result.message || 'Durum değiştirme başarısız!', 'error');
            }
            
        } catch (error) {

            showToast('Bir hata oluştu: ' + error.message, 'error');
        } finally {
            hideLoadingOverlay();
        }
    }
    
    function updateStatusBadge(ticketId, newStatus, statusDisplay) {
        const badge = document.getElementById(`status-badge-${ticketId}`);
        if (badge) {
            badge.className = `status-badge status-${newStatus}`;
            badge.textContent = statusDisplay;
            
            // Update button data
            const button = document.querySelector(`[data-ticket-id="${ticketId}"]`);
            if (button) {
                button.dataset.currentStatus = newStatus;
            }
            

        }
    }
    
    function showLoadingOverlay(message = 'Yükleniyor...') {
        // Remove existing overlay
        const existingOverlay = document.querySelector('.loading-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary mb-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="fw-medium">${message}</div>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
    
    function hideLoadingOverlay() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    function showToast(message, type = 'success') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.modern-toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `modern-toast ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
        const iconColor = type === 'success' ? 'text-success' : 'text-danger';
        
        toast.innerHTML = `
            <i class="bi bi-${icon} ${iconColor}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
        

    }
    
    // Close modal on outside click
    if (statusModal) {
        statusModal.addEventListener('click', function(event) {
            if (event.target === statusModal) {
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        });
    }
    

});
