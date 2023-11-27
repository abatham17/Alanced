from django.urls import path
from .import views


urlpatterns =[
    path('Add/Project',views.AddProjectView.as_view()),
    path('view-all/Project/',views.ViewAllProject.as_view(), name='project-filter'),
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
    path('view/freelancer-self/bid',views.ViewFreelancerSelfBid.as_view()),
    path('view/freelancer-self/project-bid/<str:pk>',views.ViewFreelancerSelfProjectBid.as_view()),
    path('Add/Freelancer/Employment',views.FreelancerAddEmploymentView.as_view()),
    path('View-all/Freelancer/Employment/<str:pk>',views.ViewAllFreelancerEmployment.as_view()),
    path('update/Freelancer/Employment/<str:pk>',views.FreelancerEmploymentUpdateView.as_view()),
    path('saved-projects/<str:pk>',views.SavedProjectsView.as_view()),
    path('View-all/SavedProjects',views.ViewAllSavedJobs.as_view()),
    path('add/subscribe', views.SubscriptionView.as_view(), name='subscribe'),
    path('user/contact-us', views.UserContactUsView.as_view(), name='contact-us'),
    path('view/client-notifications', views.ClientNotificationListView.as_view()),
    path('read/client-notification/<int:pk>', views.ClientNotificationUpdateView.as_view(), name='mark_notification_as_read'),
    path('delete/client-notification/<int:id>', views.ClientNotificationDeleteView.as_view(), name='delete-notification'),
    path('view/freelancer-notifications', views.FreelancerNotificationListView.as_view()),
    path('read/freelancer-notification/<int:pk>', views.FreelancerNotificationUpdateView.as_view()),
    path('delete/freelancer-notification/<int:id>', views.FreelancerNotificationDeleteView.as_view()),
    path('view/freelancer-all-self/bid',views.ViewFreelancerAllSelfBid.as_view()),
    path('hire/<str:pk>', views.HireFreelancerView.as_view(), name='hire-freelancer'),
    path('projects/accept/<int:pk>', views.FreelancerAcceptProjectView.as_view(), name='accept-project'),
    path('projects/reject/<int:pk>', views.FreelancerRejectProjectView.as_view(), name='reject-project'),
    path('View-all/hire-request',views.ViewAllHiringRequests.as_view()),
    path('view-all/hirer-self/Project',views.ViewAllHirerSelfProject.as_view()),
    path('View-all/invited-freelancers',views.ViewAllInvitedFreelancers.as_view()),
    path('View-all/pending-hire-request',views.ViewAllPendingHiringRequests.as_view()),
    path('View-all/freelancer-contracts',views.ViewAllFreelancerContracts.as_view()),
    path('View-all/hirer-contracts',views.ViewAllHirerContracts.as_view()),
    path('View/project-invitations-count/<int:project_id>',views.ViewInvitedFreelancersForProject.as_view()),
]
   