import json
from uuid import UUID
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from account.models import Hirer, Freelancer
from chat.models import Conversation, Message
from . serializers import MessageSerializer

if Hirer:
    User = Hirer
    print("Hirer : ",Hirer)
    print("User ---------------- : ",User.objects.filter(email = "sachin.wiz91@gmail.com"))
if Freelancer:
    print("freelancer : ",Freelancer)
    user = Freelancer
    user_id = user.objects.filter(email = "sachinsharmapeace@gmail.com")
    for i in user_id:
        print("User ---------------- : ",i.id)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)
 
class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.room_name = None
        self.user = None
        self.conversation_name = None
        self.conversation = None
 
    def connect(self):
        print("Connected!")
        # self.user = self.scope['user']
        # self.room_name = "home"
        self.accept()
        self.conversation_name=(
            f"{self.scope['url_route']['kwargs']['conversation_name']}"
        )
        self.conversation, created = Conversation.objects.get_or_create(
            name=self.conversation_name
        )
        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name
        )
        messages = self.conversation.messages.all().order_by("-timestamp")[0:10]
        message_count = self.conversation.messages.all().count()
        print("messages !!!!!!!!!! ",message_count)
        self.send_json(
            {
                "type": "last_50_messages",
                "messages": MessageSerializer(messages, many=True).data,
                "has_more": message_count > 5,
            }
        )
        # self.send_json(
        #     {
        #         "type": "welcome_message",
        #         "message": "Hey there! You've successfully connected!",
        #     }
        # )
 
    def disconnect(self, code):
        print("Disconnected!")
        return super().disconnect(code)
    
    def get_receiver(self):
        usernames = self.conversation_name.split("__")
        print("usernames ---------- >",usernames)
        usernames = [int(values) for values in usernames]
        for username in usernames:
            print("username ========== >",type(username), username)
            if username != self.sender:
                # This is the receiver
                try:
                    return user.objects.get(id = username)
                except user.DoesNotExist:
                    pass
                try:
                    return User.objects.get(id = username)
                except User.DoesNotExist:
                    pass
                # return user.objects.get(id = username) or User.objects.get(id = username)
 
    def receive_json(self, content, **kwargs):
        print("content :",content)
        message_type = content["type"]
        self.sender = content["name"]
        if message_type == "chat_message":
            # self.sender_name = User.objects.get(id = self.sender) or user.objects.get(id = self.sender)
            # if User.objects.get(id = self.sender):
            try:
                self.sender_name = User.objects.get(id = self.sender)
                print("User.objects.get(id = self.sender)",User.objects.get(id = self.sender))
            except User.DoesNotExist:
                pass
            # if user.objects.get(id = self.sender):
            try:
                self.sender_name = user.objects.get(id = self.sender)
                print("user.objects.get(id = self.sender)",user.objects.get(id = self.sender))
            except user.DoesNotExist:
                pass
            # print("sender_name ===================== : ", self.sender_name)
            # print("message from front end :",content["message"])
            # print("reciever ======= >",type(self.get_receiver))

            message = Message.objects.create(
                from_user = self.sender_name,
                to_user = self.get_receiver(),
                content = content["message"],
                conversation = self.conversation,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                # {
                #     "type": "chat_message_echo",
                #     "name": content["name"],
                #     "message": content["message"],
                # },

                {
                    "type" : "chat_message_echo",
                    "name" : self.conversation_name,
                    "message" : MessageSerializer(message).data,
                },
            )
        return super().receive_json(content, **kwargs)
    
    def chat_message_echo(self, event):
        print("event =========== :",event)
        self.send_json(event)