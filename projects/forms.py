from django import forms
from django.core.exceptions import ValidationError
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(choices=Project.STATUS_CHOICES),
        }
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith('https://github.com/') and not url.startswith('http://github.com/'):
                raise ValidationError('Ссылка должна вести на GitHub')
        return url