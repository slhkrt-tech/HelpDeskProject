from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .models import Ticket
from .forms import TicketForm, CommentForm

User = get_user_model()  # Django'nun mevcut kullanıcı modelini al

@login_required
def ticket_list(request):

    """
    Ticket listesi sayfası
    - Supervisor grubu tüm ticketları görebilir
    - Normal kullanıcı sadece kendi grubundaki ticketları görebilir
    """

    # Ticketları ilişkili alanlarıyla birlikte önceden çek

    tickets = Ticket.objects.select_related('user', 'assigned_to', 'category', 'sla')
    
    if request.user.groups.filter(name='supervisor').exists():

        # Supervisor tüm ticketları görür

        tickets = tickets.all().order_by('-created_at')
    else:

        # Normal kullanıcı sadece kendi grubu içindeki ticketları görür

        user_groups = request.user.groups.all()
        tickets = tickets.filter(user__groups__in=user_groups).distinct().order_by('-created_at')
    
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail(request, pk):

    """
    Ticket detay sayfası
    - Normal kullanıcı sadece kendi ticketını görebilir
    - Yorum ekleme işlemi yapılabilir
    - Staff kullanıcılar status ve atama güncelleyebilir
    """

    # Ticket ve ilişkili alanları getir

    ticket = get_object_or_404(
        Ticket.objects.select_related('user', 'assigned_to', 'category', 'sla'),
        pk=pk
    )

    # Yetki kontrolü: normal kullanıcı sadece kendi ticketını görebilir

    if not request.user.is_staff and ticket.user != request.user:
        return redirect('ticket_list')

    comment_form = CommentForm()

    if request.method == 'POST':

        # Yorum ekleme işlemi

        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.ticket = ticket
                c.user = request.user
                c.save()
                return redirect('ticket_detail', pk=pk)

        # Staff kullanıcı işlemleri: status veya atama güncelleme

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

    # Staff kullanıcıları template'e gönder

    staff_users = User.objects.filter(is_staff=True)
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comment_form': comment_form,
        'users': staff_users
    })

@login_required
def ticket_create(request):

    """
    Yeni ticket oluşturma sayfası
    - Form gönderildiğinde ticket kaydedilir
    - Oluşturan kullanıcı otomatik atanır
    """

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            # TODO: Yanlış bölüm senaryosu burada işlenebilir
            t.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()
    
    return render(request, 'tickets/ticket_create.html', {'form': form})

# Admin kontrol fonksiyonu

def admin_required(user):

    """
    Kullanıcının admin olup olmadığını kontrol eder
    """

    return user.is_admin()

# Support kontrol fonksiyonu

def support_required(user):

    """
    Kullanıcının destek personeli olup olmadığını kontrol eder
    """

    return user.is_support()

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):

    """
    Admin paneli sayfası
    - Sadece admin kullanıcılar görebilir
    """

    return render(request, 'admin_dashboard.html')

@login_required
@user_passes_test(support_required)
def support_dashboard(request):

    """
    Support paneli sayfası
    - Sadece destek personeli görebilir
    """
    
    return render(request, 'support_dashboard.html')

# Yeni kullanıcı kaydı için signup view

def signup(request):

    """
    Kullanıcı kayıt sayfası
    - Kayıt sonrası otomatik giriş yapılır
    """

    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth import login

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ticket_list')
    else:
        form = UserCreationForm()
    return render(request, 'tickets/signup.html', {'form': form})