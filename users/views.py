from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth import authenticate, login


class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('/projects/list/')
        return render(request, 'users/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'users/login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/projects/list/')
                return redirect(next_url)
            else:
                form.add_error(None, 'Неверный email или пароль')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/projects/list/')


class UserListView(View):
    def get(self, request):
        users = User.objects.filter(is_active=True).order_by('-created_at')
        
        paginator = Paginator(users, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'users/participants.html', {
            'participants': page_obj,
        })


class UserDetailView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_active=True)
        owned_projects = user.owned_projects.all().order_by('-created_at')[:6]
        
        return render(request, 'users/user-details.html', {
            'user': user,
            'owned_projects': owned_projects,
        })


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})
    
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.pk}/')
        return render(request, 'users/edit_profile.html', {'form': form})


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'users/change_password.html', {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect(f'/users/{request.user.pk}/')
        return render(request, 'users/change_password.html', {'form': form})