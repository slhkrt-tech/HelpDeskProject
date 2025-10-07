#category → ticket kategorileri
#SLA → servis seviyesi anlaşmaları
#ticket → destek ticket’ları
#comment → ticket yorumları

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True #uygulamanın ilk migration’ıdır

    dependencies = [ #bu migration çalışmadan önce hangi diğer migration’ların çalışması gerektiğini belirtir
        migrations.swappable_dependency(settings.AUTH_USER_MODEL), #kullanıcı tablosu
    ]

    operations = [
        migrations.CreateModel(
            name='Category', #ticket’leri sınıflandırmak için kategoriler.
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), #otomatik artan birincil anahtar
                ('name', models.CharField(max_length=100, unique=True)), #kategori adı
            ],
        ),
        migrations.CreateModel(
            name='SLA', #servis seviyesi anlaşmaları
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('response_time', models.IntegerField(help_text='Yanıt süresi (saat)')), #ticket’a yanıt süresi
                ('resolve_time', models.IntegerField(help_text='Çözüm süresi (saat)')), #ticket’ın çözülme süresi
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)), #ticket başlığı
                ('description', models.TextField()), #detaylı açıklama
                ('status', models.CharField(choices=[('new', 'Yeni'), ('open', 'Açık'), ('pending', 'Beklemede'), ('closed', 'Kapatıldı')], default='new', max_length=20)), #ticket durumu
                ('priority', models.CharField(choices=[('low', 'Düşük'), ('normal', 'Normal'), ('high', 'Yüksek'), ('urgent', 'Acil')], default='normal', max_length=20)), #öncelik
                ('created_at', models.DateTimeField(auto_now_add=True)), #oluşturulma zamanı
                ('updated_at', models.DateTimeField(auto_now=True)), #güncellenme zamanı
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)), #ticket’ı atan kişi (opsiyonel)
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tickets.category')), #ticket kategorisi (opsiyonel)
                ('sla', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tickets.sla')), #ilgili SLA (opsiyonel)
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL)), #ticket’ı açan kullanıcı
                #SET_NULL → ilgili kayıt silinirse bu alan NULL olur
                #CASCADE → ilgili kullanıcı silinirse ticket da silinir
            ],
        ),
        migrations.CreateModel(
            name='Comment', #ticket üzerindeki yorumları tutar
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()), #yorum metni
                ('created_at', models.DateTimeField(auto_now_add=True)), #yorum zamanı
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)), #yorumu yapan kullanıcı
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket')), #hangi ticket’a yazıldığı
                #related_name='comments' → ticket.comments.all() ile ticket’a bağlı yorumlara erişilir
            ],
        ),
    ]
