from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.contrib.auth.views import LoginView


@login_required(login_url='/account/login/')
def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        title = 'Profil'
        headerImg = 'header_contact.jpg'
        context = {'title': title, 'headerImg': headerImg}
        return render(request, 'account/index.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            return redirect('products:index')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

