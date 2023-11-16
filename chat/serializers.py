from rest_framework import serializers
from .models import Message, Conversation
from account.serializers import UserSerializer
from account.models import Freelancer, Hirer

User = None

if Freelancer:
    User = Freelancer

if Hirer:
    User = Hirer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ConversationSerializers(serializers.ModelSerializer):
    online = UserSerializer(many=True) 
    class Meta:
        model = Conversation
        fields = '__all__'
    
class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
        )

    def get_conversation(self, obj):
        return str(obj.conversation.id)
    
    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data
        
    def get_to_user(self, obj):
        return UserSerializer(obj.to_user).data
        
class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "first_Name", "last_message")

    def get_last_message(self, obj):
        messages = obj.message.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        print("message :",message)

        return MessageSerializer(message).data
    
    def get_other_user(self, obj):
        usernames = obj.name.split("__")
        context = {}
        for username in usernames:
            if username in usernames:
                other_user = User.objects.get(first_Name = username)
                return UserSerializer(other_user, context=context).data