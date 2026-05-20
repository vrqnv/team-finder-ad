import re

from core.mixins import GitHubURLMixin
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from users.constants import (
    EMAIL_ALREADY_EXISTS_ERROR,
    MAX_LENGTH_NAME,
    MAX_LENGTH_PHONE,
    PHONE_ALREADY_EXISTS_ERROR,
    PHONE_ERROR_MESSAGE,
    PHONE_REGEX_PATTERN,
)
from users.models import User


class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=MAX_LENGTH_NAME, required=True, label='Имя'
    )
    surname = forms.CharField(
        max_length=MAX_LENGTH_NAME, required=True, label='Фамилия'
    )
    email = forms.EmailField(
        required=True, label='Email'
    )
    phone = forms.CharField(
        max_length=MAX_LENGTH_PHONE, required=True, label='Телефон'
    )

    class Meta:
        model = User
        fields = [
            'name', 'surname', 'email', 'phone', 'password1', 'password2'
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        if not re.match(PHONE_REGEX_PATTERN, phone):
            raise ValidationError(PHONE_ERROR_MESSAGE)
        if User.objects.filter(phone=phone).exists():
            raise ValidationError(PHONE_ALREADY_EXISTS_ERROR)
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(EMAIL_ALREADY_EXISTS_ERROR)
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class UserProfileForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        if not re.match(PHONE_REGEX_PATTERN, phone):
            raise ValidationError(PHONE_ERROR_MESSAGE)
        if (User.objects.exclude(pk=self.instance.pk)
                .filter(phone=phone).exists()):
            raise ValidationError(PHONE_ALREADY_EXISTS_ERROR)
        return phone
