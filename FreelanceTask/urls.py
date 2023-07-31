from django.urls import path
from .import views


urlpatterns =[
    path('Add/Project',views.AddProjectView.as_view()),
    path('view-all/Project',views.ViewAllProject.as_view()),
    path('view/project/<str:pk>',views.ViewProjectById.as_view()),
    path('view/hirer-self/Project',views.ViewHirerSelfProject.as_view()),
    path('update/project/<str:pk>',views.ProjectUpdateView.as_view()),
    path('delete/project/<str:pk>',views.DeleteProjectView.as_view()),
]
   