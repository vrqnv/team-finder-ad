from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from users.constants import USERS_PER_PAGE
from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        login(self.request, user)
        return redirect(reverse('projects:project_list'))

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class LoginView(BaseLoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('projects:project_list')


class LogoutView(BaseLogoutView):
    next_page = 'projects:project_list'


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = USERS_PER_PAGE

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('-created_at')


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owned_projects'] = (
            self.object.owned_projects.all().order_by('-created_at')[:6]
        )
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'users:user_detail', kwargs={'user_id': self.request.user.pk}
        )


class ChangePasswordView(BasePasswordChangeView):
    template_name = 'users/change_password.html'

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Пароль успешно изменен')
        return redirect(reverse(
            'users:user_detail',
            kwargs={'user_id': self.request.user.pk}
        ))

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})
