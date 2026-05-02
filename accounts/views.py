from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect('profiles:my_page')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profiles:edit')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profiles:my_page')
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('profiles:my_page')
            error = 'Неверная эл. почта или пароль.'
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
