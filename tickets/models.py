from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Django'nun mevcut user modelini al

# ---------------------------
# Kategori modeli
# ---------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Kategori adı, benzersiz

    def __str__(self):
        return self.name  # Admin panel ve diğer yerlerde okunabilir isim

# ---------------------------
# SLA (Service Level Agreement) modeli
# ---------------------------

class SLA(models.Model):
    name = models.CharField(max_length=100, unique=True)
    response_time = models.IntegerField(help_text="Yanıt süresi (saat)")  # Yanıt süresi
    resolve_time = models.IntegerField(help_text="Çözüm süresi (saat)")   # Çözüm süresi

    def __str__(self):
        return self.name

# ---------------------------
# Ticket modeli
# ---------------------------

class Ticket(models.Model):

    # Ticket durum seçenekleri (admin ve template’de human-readable olacak)

    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('open', 'Açık'),
        ('pending', 'Beklemede'),
        ('closed', 'Kapatıldı'),
        ('wrong_section', 'Yanlış Bölüm / Kapatıldı'),  # ← Yeni: Yanlış bölüm durumunu human-readable yaptık
    ]

    # Öncelik seçenekleri

    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]

    # Ticket alanları
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')  # Durum
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sla = models.ForeignKey(SLA, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")  # Oluşturan kullanıcı
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Ardışık ticket numarası (silinmelerden etkilenmez)

    ticket_number = models.PositiveIntegerField(unique=True, blank=True, null=True)

    # Ticket kaydedilirken ardışık numara mantığı

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            last_ticket = Ticket.objects.order_by('-ticket_number').first()
            self.ticket_number = last_ticket.ticket_number + 1 if last_ticket and last_ticket.ticket_number else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.ticket_number}] {self.title}"  # Admin panelde okunabilir

    # Atanmış kullanıcı adını göster

    @property
    def assigned_to_name(self):
        return self.assigned_to.username if self.assigned_to else "Atanmamış"

# ---------------------------
# Ticket yorum modeli
# ---------------------------

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")  # Hangi ticket'a ait
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.pk} by {self.user}"