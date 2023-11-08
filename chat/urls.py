from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationsViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
