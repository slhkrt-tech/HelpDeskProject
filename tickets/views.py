from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .models import Talep  # Ticket -> Talep
from .forms import TicketForm, CommentForm  # Form isimleri aynı kalabilir

User = get_user_model()  # Django'nun mevcut kullanıcı modelini al

@login_required
def ticket_list(request):

    """
    Talep listesi sayfası
    - Supervisor grubu tüm talepleri görebilir
    - Normal kullanıcı sadece kendi grubundaki talepleri görebilir
    """
    
    talepler = Talep.objects.select_related('user', 'assigned_to', 'category', 'sla')
    
    if request.user.groups.filter(name='supervisor').exists():
        talepler = talepler.all().order_by('-created_at')
    else:
        user_groups = request.user.groups.all()
        talepler = talepler.filter(user__groups__in=user_groups).distinct().order_by('-created_at')
    
    return render(request, 'tickets/ticket_list.html', {'tickets': talepler})

@login_required
def ticket_detail(request, pk):

    """
    Talep detay sayfası
    - Normal kullanıcı sadece kendi talebini görebilir
    - Yorum ekleme işlemi yapılabilir
    - Staff kullanıcılar status ve atama güncelleyebilir
    """

    talep = get_object_or_404(
        Talep.objects.select_related('user', 'assigned_to', 'category', 'sla'),
        pk=pk
    )

    if not request.user.is_staff and talep.user != request.user:
        return redirect('ticket_list')

    comment_form = CommentForm()

    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.talep = talep  # ticket -> talep
                c.user = request.user
                c.save()
                return redirect('ticket_detail', pk=pk)

        if request.user.is_staff:
            if 'status' in request.POST:
                talep.status = request.POST.get('status')
                talep.save()
            if 'assign' in request.POST:
                assign_id = request.POST.get('assign_to')
                if assign_id:
                    try:
                        u = User.objects.get(pk=int(assign_id))
                        talep.assigned_to = u
                        talep.save()
                    except User.DoesNotExist:
                        pass
                return redirect('ticket_detail', pk=pk)

    staff_users = User.objects.filter(is_staff=True)
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': talep,
        'comment_form': comment_form,
        'users': staff_users
    })

@login_required
def ticket_create(request):

    """
    Yeni talep oluşturma sayfası
    - Form gönderildiğinde talep kaydedilir
    - Oluşturan kullanıcı otomatik atanır
    """

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

# Admin ve support kontrol fonksiyonları

def admin_required(user):
    return user.is_admin()

def support_required(user):
    return user.is_support()

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
@user_passes_test(support_required)
def support_dashboard(request):
    return render(request, 'support_dashboard.html')

# Kullanıcı kayıt view

def signup(request):
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