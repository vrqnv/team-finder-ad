import json
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q


from .models import Project, Skill
from .forms import ProjectForm


class ProjectListView(View):
    def get(self, request):
        projects = Project.objects.filter(status='open').order_by('-created_at')
        all_skills = Skill.objects.all()
        
        active_skill = request.GET.get('skill')
        if active_skill:
            projects = projects.filter(skills__name=active_skill)
        
        paginator = Paginator(projects, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'projects/project_list.html', {
            'projects': page_obj,
            'all_skills': all_skills,
            'active_skill': active_skill,
        })


class ProjectDetailView(View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return render(request, 'projects/project-details.html', {'project': project})


class ProjectCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': False
        })
    
    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.pk}/')
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': False
        })


class ProjectEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.owner
    
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=project)
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True,
            'project': project
        })
    
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.pk}/')
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True,
            'project': project
        })


class ProjectCompleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.owner and project.status == 'open'
    
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            is_participating = False
        else:
            project.participants.add(request.user)
            is_participating = True
        return JsonResponse({'status': 'ok', 'participating': is_participating})
    

class SkillAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 1:
            return JsonResponse([], safe=False)
        
        skills = Skill.objects.filter(
            name__istartswith=query
        ).order_by('name')[:10]
        
        data = [{'id': skill.id, 'name': skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class AddSkillToProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        
        if request.user != project.owner:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            skill_id = data.get('skill_id')
            skill_name = data.get('name')
        except:
            skill_id = request.POST.get('skill_id')
            skill_name = request.POST.get('name')
        
        skill = None
        created = False
        
        if skill_id:
            try:
                skill = Skill.objects.get(pk=skill_id)
            except Skill.DoesNotExist:
                return JsonResponse({'error': 'Skill not found'}, status=404)
        elif skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name.strip())
        else:
            return JsonResponse({'error': 'No skill provided'}, status=400)
        
        if skill in project.skills.all():
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
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        if skill in project.skills.all():
            project.skills.remove(skill)
            return JsonResponse({'status': 'ok', 'removed': True})
        
        return JsonResponse({'status': 'ok', 'removed': False})