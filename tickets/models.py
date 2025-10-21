# tickets/models.py
# ================================================================================
# HelpDesk Veri Modelleri
# Bu dosya veritabanında kullanılacak tabloları tanımlar:
# - Category (Kategori)
# - SLA (Servis Düzeyi Anlaşması)
# - Talep (Ticket)
# - Comment (Yorum)
# ================================================================================

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Aktif kullanıcı modelini al (CustomUser olabilir)


# -------------------------------------------------------------------------------
# Kategori Modeli
# -------------------------------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategori Adı")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"


# -------------------------------------------------------------------------------
# SLA (Servis Düzeyi Anlaşması) Modeli
# -------------------------------------------------------------------------------
class SLA(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="SLA Adı")
    response_time = models.IntegerField(help_text="Yanıt süresi (saat)", verbose_name="Yanıt Süresi (saat)")
    resolve_time = models.IntegerField(help_text="Çözüm süresi (saat)", verbose_name="Çözüm Süresi (saat)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Servis Düzeyi Anlaşması (SLA)"
        verbose_name_plural = "Servis Düzeyi Anlaşmaları"


# -------------------------------------------------------------------------------
# Talep (Ticket) Modeli
# -------------------------------------------------------------------------------
class Talep(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('seen', 'Görüldü'),
        ('open', 'Açık'),
        ('pending', 'Beklemeye Alındı'),
        ('in_progress', 'İşlemde'),
        ('resolved', 'Çözüldü'),
        ('closed', 'Kapatıldı'),
        ('wrong_section', 'Yanlış Bölüm'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]

    title = models.CharField(max_length=200, verbose_name="Talep Başlığı")
    description = models.TextField(verbose_name="Açıklama")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Durum")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name="Öncelik")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    sla = models.ForeignKey(SLA, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="SLA")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="talepler", verbose_name="Oluşturan Kullanıcı")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="atanan_talepler", verbose_name="Atanan Kullanıcı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    talep_numarasi = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name="Talep Numarası")

    def save(self, *args, **kwargs):
        # Talep numarasını otomatik oluştur
        if not self.talep_numarasi:
            last_talep = Talep.objects.order_by('-talep_numarasi').first()
            self.talep_numarasi = last_talep.talep_numarasi + 1 if last_talep and last_talep.talep_numarasi else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.talep_numarasi}] {self.title}"

    @property
    def assigned_to_name(self):
        return self.assigned_to.username if self.assigned_to else "Atanmamış"

    class Meta:
        verbose_name = "Talep"
        verbose_name_plural = "Talepler"


# -------------------------------------------------------------------------------
# Yorum (Comment) Modeli
# -------------------------------------------------------------------------------
class Comment(models.Model):
    talep = models.ForeignKey(Talep, on_delete=models.CASCADE, related_name="yorumlar", verbose_name="Talep", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return f"Yorum {self.pk} - {self.user}"

    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"