from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, UserForm, AddressForm
from .models import Profile, Address


def _ensure_profile(user):
    Profile.objects.get_or_create(user=user)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    _ensure_profile(request.user)
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    _ensure_profile(request.user)
    profile = request.user.profile
    if request.method == 'POST':
        uf = UserForm(request.POST, instance=request.user)
        pf = ProfileForm(request.POST, instance=profile)
        if uf.is_valid() and pf.is_valid():
            uf.save()
            pf.save()
            return redirect('accounts_profile')
    else:
        uf = UserForm(instance=request.user)
        pf = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'uf': uf, 'pf': pf})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            if addr.default:
                request.user.addresses.update(default=False)
            addr.save()
            return redirect('accounts_address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def address_edit(request, pk):
    addr = Address.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            a = form.save(commit=False)
            if a.default:
                request.user.addresses.update(default=False)
            a.save()
            return redirect('accounts_address_list')
    else:
        form = AddressForm(instance=addr)
    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def address_delete(request, pk):
    addr = Address.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        addr.delete()
        return redirect('accounts_address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'address': addr})


@login_required
def logout_confirm(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('/')
    return render(request, 'registration/logged_out.html')
