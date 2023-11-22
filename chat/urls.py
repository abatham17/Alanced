from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationsViewSet, MessageViewSet

# router = DefaultRouter()
# router.register(r'conversations', ConversationsViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('conversations/<str:name>',ConversationsViewSet.as_view(), name="conversations"),
    path('messages/', MessageViewSet.as_view({'get': 'list'}), name="messages")
]
