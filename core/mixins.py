from django.core.exceptions import ValidationError

from projects.constants import GITHUB_URL_PREFIXES


class GitHubURLMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith(GITHUB_URL_PREFIXES):
                raise ValidationError('Ссылка должна вести на GitHub')
        return url
