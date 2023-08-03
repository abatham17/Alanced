from django.urls import path
from .import views


urlpatterns =[
    path('Add/Project',views.AddProjectView.as_view()),
    path('view-all/Project',views.ViewAllProject.as_view()),
    path('view/project/<str:pk>',views.ViewProjectById.as_view()),
    path('view/hirer-self/Project',views.ViewHirerSelfProject.as_view()),
    path('update/project/<str:pk>',views.ProjectUpdateView.as_view()),
    path('delete/project/<str:pk>',views.DeleteProjectView.as_view()),
    path('Add/bid/<str:pk>',views.AddBidView.as_view()),
    path('View/bids/<str:pk>',views.ViewBidById.as_view()),
    path('edit/bid/<str:pk>',views.BidUpdateView.as_view()),
    path('delete/bid/<str:pk>',views.DeleteBidView.as_view()),
]
   