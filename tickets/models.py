#category → ticket kategorileri
#SLA → servis seviyesi anlaşmaları
#ticket → destek talepleri
#comment → ticket yorumları

from django.db import models 
from django.contrib.auth import get_user_model #django’nun hazır User modelini alır, custom user ile uyumlu

User = get_user_model()

class Category(models.Model): #ticket’ları sınıflandırmak için
    name = models.CharField(max_length=100, unique=True) #kategori adı
    def __str__(self): return self.name #admin ve shell’de nesne adı olarak name görünür

class SLA(models.Model): #servis seviyesi anlaşması
    name = models.CharField(max_length=100, unique=True)
    response_time = models.IntegerField(help_text="Yanıt süresi (saat)") #ticket’a yanıt süresi
    resolve_time = models.IntegerField(help_text="Çözüm süresi (saat)") #ticket çözüm süresi
    def __str__(self): return self.name

class Ticket(models.Model):
    STATUS_CHOICES = [ #ticket durumları
        ('new','Yeni'),
        ('open','Açık'),
        ('pending','Beklemede'),
        ('closed','Kapatıldı'),
    ]
    PRIORITY_CHOICES = [ #öncelik seviyeleri
        ('low','Düşük'),
        ('normal','Normal'),
        ('high','Yüksek'),
        ('urgent','Acil'),
    ]
    title = models.CharField(max_length=200) #ticket bilgisi
    description = models.TextField() #ticket bilgisi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new') #seçimli alanlar
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal') #seçimli alanlar
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True) #hangi kategoriye ait (opsiyonel)
    sla = models.ForeignKey(SLA, on_delete=models.SET_NULL, null=True, blank=True) #hangi SLA’ya bağlı (opsiyonel)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets") #ticket’ı açan kullanıcı
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets") #ticket’ı atanan kullanıcı (opsiyonel)
    created_at = models.DateTimeField(auto_now_add=True) #otomatik tarih alanları
    updated_at = models.DateTimeField(auto_now=True) #otomatik tarih alanları

    def __str__(self): #admin ve shell’de ticket [ID] Başlık formatında görünür
        return f"[{self.pk}] {self.title}"

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments") #yorum hangi ticket’a ait, related_name="comments" → ticket.comments.all() ile ulaşılır
    user = models.ForeignKey(User, on_delete=models.CASCADE) #yorumu yapan kullanıcı
    message = models.TextField() #yorum metni
    created_at = models.DateTimeField(auto_now_add=True) #yorum zamanı
    def __str__(self): #admin ve shell’de Comment 5 by user1 gibi görünür
        return f"Comment {self.pk} by {self.user}"