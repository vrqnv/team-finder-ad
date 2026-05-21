from django.conf import settings
from django.db import models
from django.urls import reverse

from projects.constants import (
    MAX_LENGTH_NAME_PROJECT,
    MAX_LENGTH_NAME_SKILL,
    STATUS_CHOICES,
    STATUS_OPEN,
)


class Skill(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME_SKILL,
        unique=True,
        verbose_name='Название навыка'
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME_PROJECT,
        verbose_name='Название проекта'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='GitHub'
    )
    status = models.CharField(
        max_length=max(len(choice[0]) for choice in STATUS_CHOICES),
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name='Статус'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )
    skills = models.ManyToManyField(
        Skill,
        related_name='projects',
        blank=True,
        verbose_name='Необходимые навыки'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project_detail',
                       kwargs={'project_id': self.pk})
