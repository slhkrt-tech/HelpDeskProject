from django.contrib import admin
from .models import Category, SLA, Ticket, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id','name','response_time','resolve_time')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id','title','status','priority','user','assigned_to','category','created_at')
    list_filter = ('status','priority','category')
    search_fields = ('title','description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','ticket','user','created_at')
    search_fields = ('message',)
