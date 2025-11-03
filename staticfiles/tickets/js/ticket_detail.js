// === ticket_detail.js ===
// Bu dosya HelpDesk sistemindeki ticket detay sayfasındaki etkileşimleri yönetir.

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', () => {
  const statusSelect = document.getElementById('statusSelect');
  const assignedToSelect = document.getElementById('assignedToSelect');
  const commentTextarea = document.getElementById('commentContent');
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  // Durum değişikliği event'i
  if (statusSelect) {
    statusSelect.addEventListener('change', e => {
      changeStatus(e.target.value);
    });
  }

  // Atanan kullanıcı değişikliği event'i
  if (assignedToSelect) {
    assignedToSelect.addEventListener('change', e => {
      updateAssignment(e.target.value);
    });
  }

  // Yorum karakter sayacı
  if (commentTextarea) {
    commentTextarea.addEventListener('input', () => {
      const max = 1000;
      const counter = document.getElementById('characterCounter');
      const len = commentTextarea.value.length;

      counter.textContent = `${len}/${max} karakter`;
      counter.className = len > max ? 'text-danger float-end'
        : len > max * 0.8 ? 'text-warning float-end'
        : 'text-muted float-end';
    });
  }

  // === Fonksiyonlar ===

  // Tek bir AJAX POST isteği gönderir
  function sendAjax(url, data) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data)
    })
      .then(r => r.json())
      .then(res => {
        if (res.status === 'success') {
          showNotification(res.message, 'success');
          setTimeout(() => location.reload(), 1000);
        } else {
          showNotification(res.message, 'error');
        }
      })
      .catch(() => showNotification('Bir hata oluştu.', 'error'));
  }

  // Durumu değiştirir
  function changeStatus(newStatus) {
    sendAjax(window.changeStatusURL, { status: newStatus });
  }

  // Atanan kullanıcıyı günceller
  function updateAssignment(assignedToId) {
    sendAjax(window.updateAssignmentURL, { assigned_to_id: assignedToId || null });
  }

  // Basit Toast bildirim sistemi
  function showNotification(message, type) {
    const alertBox = document.createElement('div');
    alertBox.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed top-0 end-0 m-3 shadow`;
    alertBox.style.zIndex = 2000;
    alertBox.textContent = message;
    document.body.appendChild(alertBox);

    setTimeout(() => alertBox.remove(), 3000);
  }
});