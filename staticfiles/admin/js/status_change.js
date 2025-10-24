// Admin Talep Durumu Değiştirme JavaScript
// ================================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Durum değiştirme butonlarına event listener ekle
    function initStatusChangeButtons() {
        const statusButtons = document.querySelectorAll('.status-change-btn');
        
        statusButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const talepId = this.dataset.talepId;
                const newStatus = this.dataset.newStatus;
                const buttonText = this.textContent;
                
                // Kullanıcıdan onay al
                if (!confirm(`Talep #${talepId} durumunu "${buttonText}" olarak değiştirmek istediğinizden emin misiniz?`)) {
                    return;
                }
                
                // Butonu devre dışı bırak
                this.disabled = true;
                this.style.opacity = '0.6';
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // AJAX isteği gönder
                const url = `/admin/tickets/talep/change_status/${talepId}/${newStatus}/`;
                
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Başarı mesajı göster
                        showMessage(data.message, 'success');
                        
                        // Sayfayı yenile (durum güncellemesi için)
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        showMessage(data.error || 'Bir hata oluştu', 'error');
                        // Butonu eski haline getir
                        resetButton(this, buttonText);
                    }
                })
                .catch(error => {
                    // Hata oluştu
                    showMessage('İstek gönderilirken bir hata oluştu', 'error');
                    // Butonu eski haline getir
                    resetButton(this, buttonText);
                });
            });
        });
    }
    
    // Butonu eski haline getir
    function resetButton(button, originalText) {
        button.disabled = false;
        button.style.opacity = '1';
        button.innerHTML = originalText;
    }
    
    // Mesaj göster
    function showMessage(message, type) {
        // Mevcut mesaj varsa kaldır
        const existingMessage = document.querySelector('.status-change-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Yeni mesaj oluştur
        const messageDiv = document.createElement('div');
        messageDiv.className = `status-change-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
        messageDiv.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 9999;
            padding: 10px 15px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: ${type === 'success' ? '#28a745' : '#dc3545'};
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            min-width: 300px;
        `;
        messageDiv.innerHTML = `
            <span>${message}</span>
            <button type="button" style="background: none; border: none; color: white; float: right; font-size: 16px;" onclick="this.parentElement.remove()">×</button>
        `;
        
        document.body.appendChild(messageDiv);
        
        // 5 saniye sonra otomatik kaldır
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    // CSRF token al
    function getCookie(name) {
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
    
    // Sayfa yüklendiğinde ve AJAX güncellemelerinden sonra butonları aktifleştir
    initStatusChangeButtons();
    
    // Django admin'in AJAX işlemlerinden sonra yeniden başlat
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('DOMNodeInserted', function() {
            // Kısa gecikme sonrası yeniden başlat
            setTimeout(initStatusChangeButtons, 100);
        });
    }
});