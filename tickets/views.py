#ticket_list → kullanıcıya ticket listesi gösterir, yetki kontrolü vardır
#ticket_detail → ticket detayları, yorum ekleme, status/atama işlemleri (admin için)
#ticket_create → yeni ticket oluşturma formu
#@login_required → tüm view’lar için giriş zorunlu
#yetki kontrolü sayesinde normal kullanıcı sadece kendi ticket’ını, agent/admin tüm ticketları görür

from django.shortcuts import render, get_object_or_404, redirect #HTML şablonunu verilerle döndürür,veritabanında nesne yoksa 404 döndürür, başka URL’ye yönlendirir
from django.contrib.auth.decorators import login_required #kullanıcı giriş yapmamışsa login sayfasına yönlendirir
from .models import Ticket
from .forms import TicketForm, CommentForm
from django.contrib.auth import get_user_model #django’nun user modelini alır

User = get_user_model()

@login_required #login zorunlu
def ticket_list(request):
    #eğer kullanıcı admin/agent ise tüm ticket'ları görsün, normal kullanıcıysa sadece kendi ticket'larını görsün
    if request.user.is_staff:  #basit: staff -> agent/admin
        tickets = Ticket.objects.all().order_by('-created_at')
    else:
        tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail(request, pk): #parametresi URL’den gelir
    ticket = get_object_or_404(Ticket, pk=pk) #ticket veritabanından çekilir, yoksa 404
    #yetki kontrolü: normal kullanıcı sadece kendi ticket'ını görsün
    if not request.user.is_staff and ticket.user != request.user:
        return redirect('ticket_list')
    comment_form = CommentForm()
    if request.method == 'POST':
        #comment ekleme veya atama/durum güncelleme
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.ticket = ticket
                c.user = request.user
                c.save()
                return redirect('ticket_detail', pk=pk)
        #agent işlemleri: status/assigned_to
        if request.user.is_staff:
            if 'status' in request.POST:
                ticket.status = request.POST.get('status')
                ticket.save()
            if 'assign' in request.POST:
                assign_id = request.POST.get('assign_to')
                if assign_id:
                    try:
                        u = User.objects.get(pk=int(assign_id))
                        ticket.assigned_to = u
                        ticket.save()
                    except User.DoesNotExist:
                        pass
                return redirect('ticket_detail', pk=pk)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'comment_form': comment_form, 'users': User.objects.filter(is_staff=True)})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})
