from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random
import os


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            name=name, 
            surname=surname, 
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
    ]
    
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар')
    phone = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\+7\d{10}$', message='Номер должен быть в формате +7XXXXXXXXXX')],
        unique=True,
        verbose_name='Телефон'
    )
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    about = models.CharField(max_length=256, blank=True, null=True, verbose_name='О себе')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f'{self.name} {self.surname}'
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)
    
    def generate_avatar(self):
        size = (200, 200)
        color = random.choice(self.COLORS)
        
        image = Image.new('RGB', size, color)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 100)
        except:
            font = ImageFont.load_default()
        
        text = self.name[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        draw.text(position, text, fill='white', font=font)
        
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue(), f'avatar_{self.email}.png')