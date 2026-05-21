import random
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    AVATAR_COLORS,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_FONT_PATH,
    AVATAR_TEXT_FONT_SIZE,
    MAX_LENGTH_ABOUT,
    MAX_LENGTH_NAME,
    MAX_LENGTH_PHONE,
    PHONE_REGEX_PATTERN,
)
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(
        max_length=MAX_LENGTH_NAME, verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=MAX_LENGTH_NAME, verbose_name='Фамилия'
    )
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар')
    phone = models.CharField(
        max_length=MAX_LENGTH_PHONE,
        validators=[
            RegexValidator(
                PHONE_REGEX_PATTERN,
                message='Номер должен быть в формате +7XXXXXXXXXX'
            )
        ],
        unique=True,
        verbose_name='Телефон'
    )
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    about = models.CharField(
        max_length=MAX_LENGTH_ABOUT,
        blank=True, null=True, verbose_name='О себе'
    )

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
        color = random.choice(AVATAR_COLORS)
        image = Image.new('RGB', AVATAR_SIZE, color)
        draw = ImageDraw.Draw(image)
        text = self.name[0].upper()

        try:
            font = ImageFont.truetype(
                AVATAR_TEXT_FONT_PATH,
                AVATAR_TEXT_FONT_SIZE,
            )
        except OSError:
            font = ImageFont.load_default(size=AVATAR_TEXT_FONT_SIZE)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (AVATAR_SIZE[0] - text_width) // 2,
            (AVATAR_SIZE[1] - text_height) // 2,
        )
        draw.text(position, text, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue(), f'avatar_{self.email}.png')
