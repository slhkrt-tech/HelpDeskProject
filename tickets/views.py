from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Talep, Category
from .forms import TicketForm
from accounts.forms import CustomUserCreationForm

@login_required
def ticket_list(request):
    """Ticket listesi: Supervisor her şeyi görür, normal kullanıcı kendi grubundakilerin taleplerini görür."""
    user = request.user
    if user.groups.filter(name='Supervisor').exists() or user.is_superuser:
        tickets = Talep.objects.all()
    else:
        group_names = [g.name for g in user.groups.all()]
        tickets = Talep.objects.filter(category__name__in=group_names)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    """Ticket detay sayfası"""
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user
    if not user.is_superuser and not user.groups.filter(name='Supervisor').exists():
        group_names = [g.name for g in user.groups.all()]
        if not ticket.category or ticket.category.name not in group_names:
            return redirect('ticket_list')
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def ticket_create(request):
    """Yeni ticket oluşturma"""
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            talep = form.save(commit=False)
            talep.user = request.user
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
    """Yeni kullanıcı kaydı"""
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
    """Admin veya staff kullanıcıların, bir kullanıcıyı gruba eklemesini sağlar"""
    user = get_object_or_404(User, pk=user_id)
    groups = Group.objects.all()
    if request.method == 'POST':
        group_id = request.POST.get('group')
        if group_id:
            group = Group.objects.get(pk=group_id)
            user.groups.add(group)
            return redirect('ticket_list')
    return render(request, 'tickets/add_user_to_group.html', {'user': user, 'groups': groups})