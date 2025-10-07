from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class SLA(models.Model):
    name = models.CharField(max_length=100, unique=True)
    response_time = models.IntegerField(help_text="Yanıt süresi (saat)")
    resolve_time = models.IntegerField(help_text="Çözüm süresi (saat)")
    def __str__(self): return self.name

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new','Yeni'),
        ('open','Açık'),
        ('pending','Beklemede'),
        ('closed','Kapatıldı'),
    ]
    PRIORITY_CHOICES = [
        ('low','Düşük'),
        ('normal','Normal'),
        ('high','Yüksek'),
        ('urgent','Acil'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sla = models.ForeignKey(SLA, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.pk}] {self.title}"

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comment {self.pk} by {self.user}"
