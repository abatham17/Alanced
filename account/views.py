from django.shortcuts import render
from .models import UserAccount,Hirer,Freelancer,Owner
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import responses,Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import LoginSerializer,HirerRegistrationSerializer,FreelancerRegistrationSerializer,HirerSelfProfileSerializer,FreelancerSelfProfileSerializer,HirerProfileUpdateSerializer,FreelancerProfileUpdateSerializer,ViewAllHirerSerializer,ViewAllFreelancerSerializer,UserChangePasswordSerializer
from rest_framework import status
from rest_framework import generics,mixins
from rest_framework.parsers import MultiPartParser,FormParser
from smtputils import Util

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
                token=get_tokens_for_user(user)
                if user.type=="HIRER":
                     login_data={"Company_Name":user.Company_Name,"first_Name":user.first_Name,"last_Name":user.last_Name,"email":user.email,"contact":user.contact,"Address":user.Address,"images_logo":'/media/'+str(user.images_logo),"social_media":user.social_media,"about":user.about,"DOB":user.DOB,"Company_Establish":user.Company_Establish,"gender":user.gender,"map":user.map}
                elif user.type=="FREELANCER":
                    login_data={"first_Name":user.first_Name,"last_Name":user.last_Name,"email":user.email,"contact":user.contact,"Address":user.Address,"images_logo":'/media/'+str(user.images_logo),"social_media":user.social_media,"skills":user.skills,"about":user.about,"DOB":user.DOB,"gender":user.gender,"map":user.map,"experience":user.experience,"qualification":user.qualification,"category":user.category}
                else:
                     return Response({'status':status.HTTP_404_NOT_FOUND,'message':'You are Not a Hirer Or Freelancer Profile','data':{}},status=status.HTTP_404_NOT_FOUND) 
                return Response({'status':status.HTTP_200_OK,'message':'Login Success','data':{'type':user.type,'token':token,'login_data':login_data}},status=status.HTTP_200_OK)
            else:
                return Response({'status':status.HTTP_404_NOT_FOUND,'message':'Email or password is not valid','data':{}},status=status.HTTP_404_NOT_FOUND)



class HirerRegistrationView(generics.CreateAPIView):
    parser_classes=[MultiPartParser,FormParser]
    serializer_class=HirerRegistrationSerializer
    

    def post(self,request,format=None):
        serializer=HirerRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            # token =get_tokens_for_user(user)
            data={
                 'email_subject':"Account Verification",
                 'body': '''
        <h1>Welcome to Freelancer </h1>
        <p>Click the button below to verify your account:</p>
        <a href="http://localhost:8000" type="button" style="border: none;color: white;padding: 10px 10px;text-align: center;text-decoration: none;display: inline-block;font-size: 16px;margin: 4px 2px;cursor:pointer;background-color: #4CAF50;border-radius:5px;"><b>Verify Account</b></a>
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
            # token =get_tokens_for_user(user)
            data={
                 'email_subject':"Account Verification",
                 'body': '''
        <h1>Welcome to Freelancer! Congratulation</h1>
        <p>Click the button below to verify your account:</p>
        <a href="http://localhost:8000" type="button" style="border: none;color: white;padding: 10px 10px;text-align: center;text-decoration: none;display: inline-block;font-size: 16px;margin: 4px 2px;cursor:pointer;background-color: #4CAF50;border-radius:5px;"><b>Verify Account</b></a>
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