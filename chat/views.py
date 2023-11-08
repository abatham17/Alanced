from django.shortcuts import render
from rest_framework.response import responses,Response

# Create your views here.

from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from . models import Conversation, Message
from . serializers import ConversationSerializers, MessageSerializer, ConversationSerializer

class ConversationsViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializers
    def conversation (self):
        serializer_class = ConversationSerializers
        return Response(serializer_class.data, status=200)

class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "first_Name"
    
    def get_queryset(self):
        queryset = Conversation.objects.filter(
            name__contains = self.request.user.first_Name
        )
        return queryset
        
    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user}
    

class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()

    def get_querset(self):
        conversation_name = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                conversation__name__contains = self.request.user.first_Name,
            ).filter(conversation__name = conversation_name).order_by("-timestamp")
        )
        return queryset