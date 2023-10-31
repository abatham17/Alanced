from django.urls import path
from .import views


urlpatterns =[
    path('login',views.LoginView.as_view()),
    path('hirer/registration',views.HirerRegistrationView.as_view()),
    path('freelancer/registration',views.FreelancerRegistrationView.as_view()),
    path('hirer/selfprofile/view',views.HirerSelfProfileView.as_view()),
    path('freelancer/selfprofile/view',views.FreelancerSelfProfileView.as_view()),
    path('hirer/profile/update',views.HirerUpdateProfileView.as_view()),
    path('freelancer/profile/update',views.FreelancerUpdateProfileView.as_view()),
    path('hirer/profile/view-all',views.AllHirerView.as_view()),
    path('freelancer/profile/view-all/',views.AllFreelancerView.as_view()),
    path('hirer/profile/Delete/<str:pk>',views.DeleteHirerView.as_view()),
    path('freelancer/profile/Delete/<str:pk>',views.DeleteFreelancerView.as_view()),
    path('change-password',views.UserChangePasswordView.as_view()),
    path('verify/<str:uid>/<str:token>/',views.AccountVerification),
    path('forgot-password', views.SendPasswordResetEmailView.as_view()),
    path('password/reset/<uid>/<token>',views.UserPasswordResetView.as_view()),
    path('google-login/', views.googleLoginView.as_view()),
    path('check-email/', views.CheckEmailExistsView.as_view()),
]