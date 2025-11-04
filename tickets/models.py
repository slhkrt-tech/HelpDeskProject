# tickets/models.py
"""
Yardım Masası Ticket Yönetimi - Veri Modelleri
=========================================

Bu modül ticket sisteminin temel veri modellerini içerir:
- Category: Talep kategorileri (Donanım, Yazılım, Ağ vs.)
- SLA: Servis düzeyi anlaşmaları ve yanıt süreleri
- Talep: Ana ticket modeli - talepler ve durumları
- Comment: Ticket yorumları ve mesajlaşma sistemi
"""

# Django temel importları
from django.db import models
from django.contrib.auth import get_user_model

# Aktif kullanıcı modelini al (CustomUser)
User = get_user_model()

# ================================================================================
# Kategori Modeli
# ================================================================================

class Category(models.Model):
    """
    Talep kategorileri modeli
    Örnek: Donanım, Yazılım, Ağ Sorunları, E-posta vb.
    """
    
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Kategori Adı",
        help_text="Talep kategorisinin adı (Donanım, Yazılım vb.)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Açıklama",
        help_text="Kategori hakkında detaylı açıklama"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']

# ================================================================================
# SLA (Servis Düzeyi Anlaşması) Modeli
# ================================================================================

class SLA(models.Model):
    """
    Servis Düzeyi Anlaşması modeli
    Yanıt ve çözüm sürelerini tanımlar
    """
    
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="SLA Adı",
        help_text="SLA seviyesinin adı (Kritik, Normal, Düşük vb.)"
    )
    response_time = models.IntegerField(
        verbose_name="Yanıt Süresi (saat)",
        help_text="İlk yanıt verilmesi gereken süre (saat cinsinden)"
    )
    resolve_time = models.IntegerField(
        verbose_name="Çözüm Süresi (saat)",
        help_text="Sorunu çözmek için verilen maksimum süre (saat cinsinden)"
    )

    def __str__(self):
        return f"{self.name} (Yanıt: {self.response_time}sa, Çözüm: {self.resolve_time}sa)"

    class Meta:
        verbose_name = "Servis Düzeyi Anlaşması (SLA)"
        verbose_name_plural = "Servis Düzeyi Anlaşmaları"
        ordering = ['response_time']

# ================================================================================
# Talep (Ticket) Modeli
# ================================================================================

class Talep(models.Model):
    """
    Ana ticket modeli - kullanıcı taleplerini ve durumlarını yönetir
    Modern iş akışı ve durum takibi içerir
    """
    
    # Ticket durum seçenekleri
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

    # Öncelik seviyeleri
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]

    # Temel ticket bilgileri
    title = models.CharField(
        max_length=200, 
        verbose_name="Talep Başlığı",
        help_text="Kısa ve açıklayıcı ticket başlığı"
    )
    description = models.TextField(
        verbose_name="Açıklama",
        help_text="Sorunun detaylı açıklaması"
    )
    
    # Durum ve öncelik bilgileri
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new', 
        verbose_name="Durum",
        help_text="Ticket'ın mevcut durumu"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normal', 
        verbose_name="Öncelik",
        help_text="Ticket'ın önem seviyesi"
    )
    
    # İlişkili modeller
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Kategori",
        help_text="Ticket kategorisi"
    )
    sla = models.ForeignKey(
        SLA, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="SLA",
        help_text="Uygulanan servis düzeyi anlaşması"
    )
    
    # Kullanıcı ilişkileri
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="talepler", 
        verbose_name="Oluşturan Kullanıcı",
        help_text="Ticket'ı oluşturan kullanıcı"
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="atanan_talepler", 
        verbose_name="Atanan Kullanıcı",
        help_text="Ticket'ı çözecek olan kullanıcı"
    )
    
    # Zaman damgaları
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Güncellenme Tarihi"
    )
    
    # Benzersiz ticket numarası
    talep_numarasi = models.PositiveIntegerField(
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name="Talep Numarası",
        help_text="Sistem tarafından otomatik atanan benzersiz numara"
    )

    def save(self, *args, **kwargs):
        """
        Kaydetme işlemi - otomatik talep numarası ataması
        """
        # Talep numarasını otomatik oluştur
        if not self.talep_numarasi:
            last_talep = Talep.objects.order_by('-talep_numarasi').first()
            if last_talep and last_talep.talep_numarasi:
                self.talep_numarasi = last_talep.talep_numarasi + 1
            else:
                self.talep_numarasi = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.talep_numarasi}] {self.title}"

    @property
    def assigned_to_name(self):
        """
        Atanan kullanıcı adını döndürür
        """
        return self.assigned_to.username if self.assigned_to else "Atanmamış"

    class Meta:
        verbose_name = "Talep"
        verbose_name_plural = "Talepler"
        ordering = ['-created_at']  # En yeni ticket'lar önce

# ================================================================================
# Yorum (Comment) Modeli
# ================================================================================

class Comment(models.Model):
    """
    Ticket yorumları ve mesajlaşma sistemi
    Kullanıcılar arası iletişimi sağlar
    """
    
    # İlişkili ticket
    talep = models.ForeignKey(
        Talep, 
        on_delete=models.CASCADE, 
        related_name="yorumlar", 
        verbose_name="Talep",
        null=True, 
        blank=True,
        help_text="Yorumun ait olduğu ticket"
    )
    
    # Yorum sahibi
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Kullanıcı",
        help_text="Yorumu yazan kullanıcı"
    )
    
    # Yorum içeriği
    message = models.TextField(
        verbose_name="Mesaj",
        help_text="Yorum veya mesaj içeriği"
    )
    
    # Zaman damgası
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Oluşturulma Tarihi"
    )

    def __str__(self):
        return f"Yorum {self.pk} - {self.user.username}"

    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"
        ordering = ['created_at']  # Eski yorumlar önce