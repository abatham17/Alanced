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
    path('view-all/hirer/Membership-plans',views.ViewAllHirerMembership.as_view()),
    path('view-all/freelancer/Membership-plans',views.ViewAllFreelancerMembership.as_view()),
    path('Add/Review/<str:pk>',views.AddReviewsView.as_view()),
    path('View-all/Review/<str:pk>',views.ViewAllReviews.as_view()),
    path('Edit/Review/<str:pk>',views.EditReviews.as_view()),
    path('delete/review/<str:pk>',views.DeleteReviews.as_view()),
    path('Add/Freelancer/Self-Project',views.FreelancerAddProjectView.as_view()),
    path('View-all/Freelancer/Self-Project/<str:pk>',views.ViewAllFreelancerProjects.as_view()),
    path('update/Freelancer/Self-project/<str:pk>',views.FreelancerProjectUpdateView.as_view()),
    path('delete/freelancer/project/<str:pk>',views.DeleteFreelancerProjectView.as_view()),
]
   