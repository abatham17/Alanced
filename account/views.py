from django.shortcuts import render,redirect
from .models import UserAccount,Hirer,Freelancer,Owner
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import responses,Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import LoginSerializer,HirerRegistrationSerializer,FreelancerRegistrationSerializer,HirerSelfProfileSerializer,FreelancerSelfProfileSerializer,HirerProfileUpdateSerializer,FreelancerProfileUpdateSerializer,ViewAllHirerSerializer,ViewAllFreelancerSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordResetSerializer
from rest_framework import status
from rest_framework import generics,mixins
from rest_framework.parsers import MultiPartParser,FormParser
from smtputils import Util
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(GenericAPIView):
    serializer_class=LoginSerializer
    
    def post(self,request,format=None):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.data.get('email')
            password =serializer.data.get('password')
            try:
                user_obj=UserAccount.objects.get(email=email)
            except:
                return Response({'status':status.HTTP_404_NOT_FOUND,'message':'Please register user first','data':{}},status=status.HTTP_404_NOT_FOUND)
            if user_obj.Block==True:
                return Response({'status':status.HTTP_401_UNAUTHORIZED,'message':'Your user Id is Block','data':{}},status=status.HTTP_401_UNAUTHORIZED)
            user=authenticate(email=email,password=password)
            if user is not None:
                if user.is_verified==True:
                    token=get_tokens_for_user(user)
                    if user.type=='OWNER':
                        login_data={"Company_Name":user.Company_Name,"first_Name":user.first_Name,"last_Name":user.last_Name,"email":user.email,"contact":user.contact,"Address":user.Address,"images_logo":'/media/'+str(user.images_logo),"gender":user.gender}
                    elif user.type=="HIRER":
                        login_data={"Company_Name":user.Company_Name,"first_Name":user.first_Name,"last_Name":user.last_Name,"email":user.email,"contact":user.contact,"Address":user.Address,"images_logo":'/media/'+str(user.images_logo),"social_media":user.social_media,"about":user.about,"DOB":user.DOB,"Company_Establish":user.Company_Establish,"gender":user.gender,"map":user.map}
                    else:
                        login_data={"first_Name":user.first_Name,"last_Name":user.last_Name,"email":user.email,"contact":user.contact,"Address":user.Address,"images_logo":'/media/'+str(user.images_logo),"social_media":user.social_media,"skills":user.skills,"about":user.about,"DOB":user.DOB,"gender":user.gender,"map":user.map,"experience":user.experience,"qualification":user.qualification,"category":user.category}  
                    return Response({'status':status.HTTP_200_OK,'message':'Login Success','data':{'type':user.type,'token':token,'login_data':login_data}},status=status.HTTP_200_OK)
                else:
                    return Response({'status':status.HTTP_400_BAD_REQUEST,'message':"Your Account is not verified, Please Verify your Account",'data':{}},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status':status.HTTP_404_NOT_FOUND,'message':'Email or password is not valid','data':{}},status=status.HTTP_404_NOT_FOUND)



class HirerRegistrationView(generics.CreateAPIView):
    parser_classes=[MultiPartParser,FormParser]
    serializer_class=HirerRegistrationSerializer
    

    def post(self,request,format=None):
        serializer=HirerRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            email=serializer.data.get('email')
            usr = Hirer.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(usr.id))
            token =default_token_generator.make_token(usr)
            data={
                 'email_subject':"Account Verification",
                 'body': '''
        <h1>Welcome to Alanced</h1>
        <p>Click the button below to verify your account:</p>
        <a href="https://aparnawiz91.pythonanywhere.com/account/verify/'''+uid+'''/'''+token+'''" type="button" style="border: none;color: white;padding: 10px 10px;text-align: center;text-decoration: none;display: inline-block;font-size: 16px;margin: 4px 2px;cursor:pointer;background-color: #4CAF50;border-radius:5px;"><b>Verify Account</b></a>
    ''',
                 'to_email': request.data['email']
            }
            Util.send_email(data)
            return Response({'status':status.HTTP_200_OK,'message':'Registration Sucessful, Verification link sent on your email'},status=status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}},status=status.HTTP_400_BAD_REQUEST)
    


class FreelancerRegistrationView(generics.CreateAPIView):
    parser_classes=[MultiPartParser,FormParser]
    serializer_class=FreelancerRegistrationSerializer
    

    def post(self,request,format=None):
        serializer=FreelancerRegistrationSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            email=serializer.data.get('email')
            usr = Freelancer.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(usr.id))
            token =default_token_generator.make_token(usr)
            # token =get_tokens_for_user(user)
            data={
                 'email_subject':"Account Verification",
                 'body': '''
        <h1>Welcome to Alanced</h1>
        <p>Click the button below to verify your account:</p>
    ''',
                 'to_email': request.data['email']
            }
            Util.send_email(data)
            return Response({'status':status.HTTP_200_OK,'message':'Registration Sucessful, Verification link sent on your email'},status=status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}},status=status.HTTP_400_BAD_REQUEST)


class HirerSelfProfileView(GenericAPIView,mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = HirerSelfProfileSerializer


    def get(self,request,*args,**kwargs):
        if request.user.type!="HIRER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Hirer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        user = Hirer.objects.filter(id=self.request.user.id).values('id','email','first_Name','last_Name','contact','Address','DOB','gender','Company_Name','type','images_logo','Company_Establish','social_media','map')
        userlist=[]
        for i in user:
            userlist.append({'id':i['id'],'email':i['email'],'first_Name':i['first_Name'],'last_Name':i['last_Name'],'contact':i['contact'],'Address':i['Address'],'DOB':i['DOB'],'gender':i['gender'],'Company_Name':i['Company_Name'],'type':i['type'],'images_logo':'/media/'+i['images_logo'],'Company_Establish':i['Company_Establish'],'social_media':i['social_media'],'map':i['map']})
        return Response({'status':status.HTTP_200_OK,'message':"Ok",'data':userlist},status=status.HTTP_200_OK)
    


class FreelancerSelfProfileView(GenericAPIView,mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerSelfProfileSerializer


    def get(self,request,*args,**kwargs):
        if request.user.type!="FREELANCER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Freelancer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        user = Freelancer.objects.filter(id=self.request.user.id).values('id','email','first_Name','last_Name','contact','Address','DOB','gender','type','images_logo','social_media','map','experience','qualification','skills','category')
        userlist=[]
        for i in user:
            userlist.append({'id':i['id'],'email':i['email'],'first_Name':i['first_Name'],'last_Name':i['last_Name'],'contact':i['contact'],'Address':i['Address'],'DOB':i['DOB'],'gender':i['gender'],'experience':i['experience'],'type':i['type'],'images_logo':'/media/'+i['images_logo'],'qualification':i['qualification'],'social_media':i['social_media'],'map':i['map'],'skills':i['skills'],'category':i['category']})
        return Response({'status':status.HTTP_200_OK,'message':"Ok",'data':userlist},status=status.HTTP_200_OK)


class HirerUpdateProfileView(GenericAPIView,mixins.UpdateModelMixin):
    parser_classes= [MultiPartParser,FormParser]
    permission_classes = [IsAuthenticated]
    serializer_class= HirerProfileUpdateSerializer

    def put(self,request,*args,**kwargs):
        if request.user.type!="HIRER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Hirer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        user=Hirer.objects.get(id=self.request.user.id)
        serializer=self.serializer_class(instance=user,data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'message':"Your profile Updated successfully",'data':serializer.data},status=status.HTTP_200_OK)
        


class FreelancerUpdateProfileView(GenericAPIView,mixins.UpdateModelMixin):
    parser_classes= [MultiPartParser,FormParser]
    permission_classes = [IsAuthenticated]
    serializer_class= FreelancerProfileUpdateSerializer

    def put(self,request,*args,**kwargs):
        if request.user.type!="FREELANCER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Freelancer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        user=Freelancer.objects.get(id=self.request.user.id)
        serializer=self.serializer_class(instance=user,data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'message':"Your profile Updated successfully",'data':serializer.data},status=status.HTTP_200_OK)
        

class AllHirerView(generics.ListAPIView):
    serializer_class=ViewAllHirerSerializer
    def get(self,request,format=None):
        Hirers_data=Hirer.objects.all().values()
        hirerlist=[]
        for i in Hirers_data:
            hirerlist.append({'id':i['id'],'email':i['email'],'first_Name':i['first_Name'],'last_Name':i['last_Name'],'contact':i['contact'],'Address':i['Address'],'DOB':i['DOB'],'gender':i['gender'],'Company_Name':i['Company_Name'],'type':i['type'],'images_logo':'/media/'+i['images_logo'],'Company_Establish':i['Company_Establish'],'social_media':i['social_media'],'map':i['map']})
        return Response({'status':status.HTTP_200_OK,'message':"Ok",'data':hirerlist},status=status.HTTP_200_OK)    
        

class AllFreelancerView(generics.ListAPIView):
    serializer_class=ViewAllFreelancerSerializer
    def get(self,request,format=None):
        Freelancer_data=Freelancer.objects.all().values()
        Freelancerlist=[]
        for i in Freelancer_data:
            Freelancerlist.append({'id':i['id'],'email':i['email'],'first_Name':i['first_Name'],'last_Name':i['last_Name'],'contact':i['contact'],'Address':i['Address'],'DOB':i['DOB'],'gender':i['gender'],'experience':i['experience'],'type':i['type'],'images_logo':'/media/'+i['images_logo'],'qualification':i['qualification'],'social_media':i['social_media'],'map':i['map'],'skills':i['skills'],'category': i['category']})
        return Response({'status':status.HTTP_200_OK,'message':"Ok",'data':Freelancerlist},status=status.HTTP_200_OK)         
    

class DeleteHirerView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes=[IsAuthenticated]
    queryset=Hirer.objects.all()
    def delete(self,request,*args,**kwargs):
        Chk_hirer=Hirer.objects.filter(id=kwargs['pk'])
        if Chk_hirer.exists():
            hirer_obj=Hirer.objects.get(id=kwargs['pk'])
            if hirer_obj.id==request.user.id:
                if request.user.Block==True:  
                    return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked','data':{}}, status=status.HTTP_403_FORBIDDEN)
                del_item=self.destroy(self,request,*args,**kwargs)
                return Response ({'status': status.HTTP_204_NO_CONTENT,'message':'Your Profile Deleted Successfully','data':{str(del_item)}}, status=status.HTTP_204_NO_CONTENT)    
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'This is not Your Profile','data':{}}, status=status.HTTP_404_NOT_FOUND)           
        return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND) 


class DeleteFreelancerView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes=[IsAuthenticated]
    queryset=Freelancer.objects.all()
    def delete(self,request,*args,**kwargs):
        Chk_freelancer=Freelancer.objects.filter(id=kwargs['pk'])
        if Chk_freelancer.exists():
            freelancer_obj=Freelancer.objects.get(id=kwargs['pk'])
            if freelancer_obj.id==request.user.id:
                if request.user.Block==True:  
                    return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked','data':{}}, status=status.HTTP_403_FORBIDDEN)
                del_item=self.destroy(self,request,*args,**kwargs)
                return Response ({'status': status.HTTP_204_NO_CONTENT,'message':'Your Profile Deleted Successfully','data':{str(del_item)}}, status=status.HTTP_204_NO_CONTENT)    
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'This is not Your Profile','data':{}}, status=status.HTTP_404_NOT_FOUND)           
        return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)        


class UserChangePasswordView(generics.CreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class=UserChangePasswordSerializer
   def post(self, request, format=None):
    #   chk_pass=UserAccount.objects.all()
    #   print(chk_pass[0].password)
      serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
      if serializer.is_valid(raise_exception=True):
          return Response({'status':status.HTTP_200_OK,'message':"Your Password Changed Successfully"},status=status.HTTP_200_OK)
      return Response({'status':status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}},status=status.HTTP_400_BAD_REQUEST)


def AccountVerification(request,uid,token):
    uid = urlsafe_base64_decode(uid).decode()
    user=UserAccount.objects.get(id=uid)
    if default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        return redirect('https://aparnawiz91.pythonanywhere.com/') 
    

class SendPasswordResetEmailView(generics.CreateAPIView):
  serializer_class=SendPasswordResetEmailSerializer
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'status':status.HTTP_200_OK,'message':"Password Reset link send. Please check your Email"},status=status.HTTP_200_OK)
  

class UserPasswordResetView(generics.CreateAPIView):
  serializer_class=UserPasswordResetSerializer
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'status':status.HTTP_200_OK,'message':"Password Reset Successfully"},status=status.HTTP_200_OK)      