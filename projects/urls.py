from django.urls import path

from projects import views


app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(),
         name='project_list'),
    path('create-project/', views.ProjectCreateView.as_view(),
         name='project_create'),
    path('<int:project_id>/', views.ProjectDetailView.as_view(),
         name='project_detail'),
    path('<int:project_id>/edit/', views.ProjectEditView.as_view(),
         name='project_edit'),
    path('<int:project_id>/complete/', views.ProjectCompleteView.as_view(),
         name='project_complete'),
    path(
        '<int:project_id>/toggle-participate/',
        views.ToggleParticipateView.as_view(),
        name='toggle_participate'
    ),
    path('skills/', views.SkillAutocompleteView.as_view(),
         name='skill_autocomplete'),
    path(
        '<int:project_id>/skills/add/',
        views.AddSkillToProjectView.as_view(),
        name='add_skill'
    ),
    path(
        '<int:project_id>/skills/<int:skill_id>/remove/',
        views.RemoveSkillFromProjectView.as_view(),
        name='remove_skill'
    ),
]
