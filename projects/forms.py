from django import forms

from core.mixins import GitHubURLMixin
from projects.constants import STATUS_CHOICES
from projects.models import Project


class ProjectForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(choices=STATUS_CHOICES),
        }
