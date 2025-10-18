from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .models import Talep, Category
from .forms import TicketForm
from accounts.forms import CustomUserCreationForm

User = get_user_model()  # Projede kullanılan özel kullanıcı modelini alır (CustomUser)

@login_required
def ticket_list(request):
    """Ticket listesini döndürür.

    Davranış:
    - Eğer kullanıcı Supervisor grubundaysa veya superuser ise tüm talepler gösterilir.
    - Normal kullanıcı ise kendi talepleri ve aynı gruptaki diğer kullanıcıların talepleri gösterilir.

    Bu fonksiyon login_required dekoratörü ile korunur.
    """
    user = request.user
    if user.groups.filter(name='Supervisor').exists() or user.is_superuser:
        tickets = Talep.objects.all()
    else:
        # Kullanıcının kendi gruplarındaki diğer kullanıcıları al
        group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
        tickets = Talep.objects.filter(user=user) | Talep.objects.filter(user__in=group_users)
        tickets = tickets.distinct()  # Tekrarları önlemek için
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    """Belirli bir talebin detay sayfasını gösterir.

    Erişim kontrolü:
    - Sadece talebi oluşturan kullanıcı, aynı gruptaki kullanıcılar veya Supervisor/superuser görüntüleyebilir.
    """
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user
    if not user.is_superuser and not user.groups.filter(name='Supervisor').exists():
        group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
        if ticket.user != user and ticket.user not in group_users:
            return redirect('ticket_list')
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def ticket_create(request):
    """Yeni bir talep (ticket) oluşturma formunu işler ve kaydeder.

    - POST isteklerinde form doğrulanır, kullanıcı talep sahibi olarak atanır.
    - Eğer kullanıcının grup adı varsa, aynı isimde bir Category varsa otomatik atama yapılır.
    - Başarılı kayıt sonrası ticket listesine yönlendirir.
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            talep = form.save(commit=False)
            talep.user = request.user  # talebi oluşturan kullanıcıyı ata
            # Kullanıcının grubu varsa Category'yi grup adına göre ata
            if request.user.groups.exists():
                group_name = request.user.groups.first().name
                category = Category.objects.filter(name=group_name).first()
                if category:
                    talep.category = category
            talep.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})


def signup(request):
    """Kayıt (signup) sayfası ve kullanıcı oluşturma işlemi.

    - Başarılı kayıt sonrası kullanıcı otomatik olarak giriş yapılır ve talepler sayfasına yönlendirilir.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ticket_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def add_user_to_group(request, user_id):
    """Belirlenen kullanıcıyı (user_id) bir gruba eklemeyi sağlar.

    Bu işlem yalnızca staff veya superuser tarafından yapılabilir (user_passes_test ile korunur).
    """
    user = get_object_or_404(User, pk=user_id)
    groups = Group.objects.all()
    if request.method == 'POST':
        group_id = request.POST.get('group')
        if group_id:
            group = Group.objects.get(pk=group_id)
            user.groups.add(group)
            return redirect('ticket_list')
    return render(request, 'tickets/add_user_to_group.html', {'user': user, 'groups': groups})