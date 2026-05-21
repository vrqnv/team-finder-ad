import json
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from projects.constants import (
    PROJECTS_PER_PAGE,
    SKILLS_AUTOCOMPLETE_LIMIT,
    STATUS_CLOSED,
    STATUS_OPEN,
)
from projects.forms import ProjectForm
from projects.models import Project, Skill


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        projects = (
            Project.objects
            .filter(status=STATUS_OPEN)
            .select_related('owner')
            .prefetch_related('participants', 'skills')
            .order_by('-created_at')
        )

        active_skill = self.request.GET.get('skill')
        if active_skill:
            projects = projects.filter(skills__name=active_skill)

        return projects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = Skill.objects.all()
        context['active_skill'] = self.request.GET.get('skill')
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('owner')
            .prefetch_related('participants')
        )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect(project.get_absolute_url())


class ProjectEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'
    pk_url_kwarg = 'project_id'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['project'] = self.get_object()
        return context


class ProjectCompleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs.get('project_id'))
        is_owner = self.request.user == project.owner
        is_open = project.status == STATUS_OPEN
        return is_owner and is_open

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': STATUS_CLOSED})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        is_participating = project.participants.filter(
            pk=request.user.pk
        ).exists()
        if is_participating:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)
        return JsonResponse({
            'status': 'ok',
            'participating': is_participating
        })


class SkillAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 1:
            return JsonResponse([], safe=False)

        skills = Skill.objects.filter(
            name__istartswith=query
        ).order_by('name')[:SKILLS_AUTOCOMPLETE_LIMIT]

        data = [{'id': skill.id, 'name': skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class AddSkillToProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)

        if request.user != project.owner:
            return JsonResponse(
                {'error': 'Permission denied'},
                status=HTTPStatus.FORBIDDEN
            )

        try:
            data = json.loads(request.body)
            skill_id = data.get('skill_id')
            skill_name = data.get('name')
        except Exception:
            skill_id = request.POST.get('skill_id')
            skill_name = request.POST.get('name')

        created = False

        if skill_id:
            try:
                skill = Skill.objects.get(pk=skill_id)
            except Skill.DoesNotExist:
                return JsonResponse(
                    {'error': 'Skill not found'},
                    status=HTTPStatus.NOT_FOUND
                )
        elif skill_name:
            skill, created = Skill.objects.get_or_create(
                name=skill_name.strip()
            )
        else:
            return JsonResponse(
                {'error': 'No skill provided'},
                status=HTTPStatus.BAD_REQUEST
            )

        if project.skills.filter(pk=skill.pk).exists():
            return JsonResponse({
                'skill_id': skill.id,
                'created': created,
                'added': False
            })

        project.skills.add(skill)

        return JsonResponse({
            'skill_id': skill.id,
            'created': created,
            'added': True
        })


class RemoveSkillFromProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id, skill_id):
        project = get_object_or_404(Project, pk=project_id)
        skill = get_object_or_404(Skill, pk=skill_id)

        if request.user != project.owner:
            return JsonResponse(
                {'error': 'Permission denied'},
                status=HTTPStatus.FORBIDDEN
            )

        if project.skills.filter(pk=skill.pk).exists():
            project.skills.remove(skill)
            return JsonResponse({'status': 'ok', 'removed': True})

        return JsonResponse({'status': 'ok', 'removed': False})
