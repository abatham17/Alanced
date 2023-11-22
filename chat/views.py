from django.shortcuts import render
from rest_framework.response import responses,Response
import uuid
from .paginaters import MessagePagination

# Create your views here.

from rest_framework.generics import GenericAPIView
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from . models import Conversation, Message
from . serializers import ConversationSerializers, MessageSerializer, ConversationSerializer
from rest_framework import status

class ConversationsViewSet(RetrieveModelMixin, GenericAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializers
    def conversation (self):
        serializer_class = ConversationSerializers
        return Response(serializer_class.data, status=200)
    
    def get(self,*args,**kwargs):
        names = Conversation.objects.all()
        AllNames = []
        AllMessages = []
        for i in names:
            if len(i.name.split("__")) == 2:
                if i.name.split('__')[0] == kwargs['name'] or i.name.split('__')[1] == kwargs['name']:
                    print('i',i.name)
                    messages = Message.objects.filter(conversation = i.id).order_by("-timestamp")[0:1]
                    for j in messages:
                        from_user = {}
                        to_user ={}
                        for key, value in MessageSerializer(j).data['from_user'].items():
                            if key == "password" or key == "date_of_creation" or key == "is_superuser":
                                continue
                            print("key",key)
                            from_user[key] = value
                            print("-------------- >",from_user)
                        for key, value in MessageSerializer(j).data['to_user'].items():
                            if key == "password" or key == "date_of_creation" or key == "is_superuser":
                                continue
                            print("key",key)
                            to_user[key] = value
                            print("-------------- >",to_user)
                        AllMessages.append({"id":j.id, "conversation":j.conversation.id, "from_user":from_user, "to_user":to_user, "content":j.content, "timestamp": j.timestamp, "read":j.read, "name": i.name})
                        # print("AllMessages : ", AllMessages)
                        print("messages ====== : ",j.id,"------",j.conversation,j.from_user,j.to_user,j.content,j.timestamp,j.read)
                    AllNames.append({"id":i.id,"name":i.name,"online":ConversationSerializers(i).data['online']})
        return Response({'status': status.HTTP_200_OK, 'data': AllMessages})

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
    queryset = Message.objects.all()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                conversation__name__contains = conversation_name
            ).filter(conversation__name = conversation_name).order_by("-timestamp")
        )
        return queryset