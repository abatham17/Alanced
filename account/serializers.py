from rest_framework import serializers
from .models import UserAccount,Hirer,Owner,Freelancer
from django.contrib.auth.hashers import make_password,check_password
from twilio.rest import Client



class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model =UserAccount
        fields=['email','password']


class HirerRegistrationSerializer(serializers.ModelSerializer):
    first_Name=serializers.CharField(max_length=25)
    last_Name=serializers.CharField(max_length=25)
    Address=serializers.CharField(max_length=100)
    DOB=serializers.DateField()
    gender=serializers.ChoiceField(choices=["Male","Female"])
    about=serializers.CharField(max_length=200)
    Company_Establish=serializers.DateField()
    social_media=serializers.URLField()
    map=serializers.URLField()
    Company_Name=serializers.CharField(max_length=100)
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=Hirer
        fields=['email','first_Name','last_Name','contact','about','Company_Establish','social_media','map','Address','DOB','gender','Company_Name','password','password2','images_logo']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        return attrs
    
    def create(self, validated_data):
        return Hirer.objects.create(email=self.validated_data['email'],password=make_password(self.validated_data['password']),first_Name=self.validated_data['first_Name'],last_Name=self.validated_data['last_Name'],contact=self.validated_data['contact'],about=self.validated_data['about'],Company_Establish=self.validated_data['Company_Establish'],social_media=self.validated_data['social_media'],map=self.validated_data['map'],Address=self.validated_data['Address'],DOB=self.validated_data['DOB'],gender=self.validated_data['gender'],Company_Name=self.validated_data['Company_Name'],images_logo=validated_data.get('images_logo'))
    


class FreelancerRegistrationSerializer(serializers.ModelSerializer):
    first_Name=serializers.CharField(max_length=25)
    last_Name=serializers.CharField(max_length=25)
    Address=serializers.CharField(max_length=100)
    DOB=serializers.DateField()
    gender=serializers.ChoiceField(choices=["Male","Female"])
    about=serializers.CharField(max_length=200)
    experience=serializers.IntegerField()
    qualification=serializers.CharField(max_length=100)
    social_media=serializers.URLField()
    map=serializers.URLField()
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    skills = serializers.ListField(child=serializers.CharField())
    category = serializers.ChoiceField(choices=["Web_development","Mobile_development","Web_designing","Software_development","Ui_Ux_designing","Logo_Designing","Graphics_designing","Cloud_computing","AI_ML","Data_Science"])
    class Meta:
        model=Freelancer
        fields=['email','first_Name','last_Name','contact','about','social_media','map','Address','DOB','gender','password','password2','images_logo','experience','qualification','skills','category']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        return attrs
    
    def create(self, validated_data):
       x= Freelancer.objects.create(email=self.validated_data['email'],password=make_password(self.validated_data['password']),first_Name=self.validated_data['first_Name'],last_Name=self.validated_data['last_Name'],contact=self.validated_data['contact'],about=self.validated_data['about'],social_media=self.validated_data['social_media'],map=self.validated_data['map'],Address=self.validated_data['Address'],DOB=self.validated_data['DOB'],gender=self.validated_data['gender'],images_logo=validated_data.get('images_logo'),experience=self.validated_data['experience'],qualification=self.validated_data['qualification'],skills=self.validated_data['skills'],category=self.validated_data['category'])
       x.save()

    #    account_sid = "AC3dba40f693ec1a81aa10b122629100fa"
    #    auth_token  = "068a5bc902f4f4271958a21c5534f2ea"

    #    client = Client(account_sid, auth_token)
    #    message = client.messages.create(
    #          body="Congratulation! Your Registration Sucessfull",
    #          from_='+17623549671',
    #          to='+917987893465') 

       return validated_data
    
class HirerSelfProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hirer
        fields =['id','email','first_Name','last_Name','contact','Address','DOB','gender','Company_Name','type','images_logo','Company_Establish','social_media','map']

    def validate(self, attrs):
        return attrs
    

    
class FreelancerSelfProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields =['id','email','first_Name','last_Name','contact','Address','DOB','gender','type','images_logo','social_media','map','experience','qualification','skills','category']

    def validate(self, attrs):
        return attrs
       

class HirerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hirer
        fields=['email','first_Name','last_Name','contact','Address','DOB','gender','Company_Name','images_logo','Company_Establish','social_media','map']

    def validate(self, attrs):
        return attrs
    

class FreelancerProfileUpdateSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(child=serializers.CharField())
    class Meta:
        model = Freelancer
        fields=['email','first_Name','last_Name','contact','Address','DOB','gender','images_logo','social_media','map','experience','qualification','skills','category']

    def validate(self, attrs):
        return attrs
    

class ViewAllHirerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Hirer
        fields=['id','email','first_Name','last_Name','contact','Address','DOB','gender','Company_Name','type','images_logo','Company_Establish','social_media','map']
        
    def validate(self, attrs):
        return attrs     
    

class ViewAllFreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Freelancer
        fields=['id','email','first_Name','last_Name','contact','Address','DOB','gender','type','images_logo','social_media','map','experience','qualification','skills','category']
        
    def validate(self, attrs):
        return attrs     
    

class UserChangePasswordSerializer(serializers.Serializer):
  password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
  new_password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
  confirm_new_password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
  class Meta:
    model=UserAccount
    fields=['password','new_password','confirm_new_password']
    extra_kwargs={
            'new_password':{'write_only':True},
            'confirm_new_password':{'write_only':True}
        }

  def validate(self, attrs):
    password=attrs.get('password')
    new_password=attrs.get('new_password')
    confirm_new_password=attrs.get('confirm_new_password')
    user=self.context.get('user')
    # print(user)
    if new_password != confirm_new_password:
      raise serializers.ValidationError("New Password and Confirm New Password doesn't match")
    if not check_password(password, user.password):
        raise serializers.ValidationError("Old password is not correct")
    user.set_password(new_password)
    user.save()
    return attrs 
  

class AccountVerificationerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields =['is_verified']

    def validate(self, attrs):
        return attrs