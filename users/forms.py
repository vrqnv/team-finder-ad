from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User
import re


class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=124, required=True, label='Имя')
    surname = forms.CharField(max_length=124, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=12, required=True, label='Телефон')
    
    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'phone', 'password1', 'password2']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        if not re.match(r'^\+7\d{10}$', phone):
            raise ValidationError('Номер должен быть в формате +7XXXXXXXXXX')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        if not re.match(r'^\+7\d{10}$', phone):
            raise ValidationError('Номер должен быть в формате +7XXXXXXXXXX')
        if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and not url.startswith('https://github.com/') and not url.startswith('http://github.com/'):
            raise ValidationError('Ссылка должна вести на GitHub')
        return url