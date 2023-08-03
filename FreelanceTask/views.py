from django.shortcuts import render
from . models import Project,Bid
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import AddProjectSerializer,ViewAllProjectSerializer,ProjectUpdateSeralizer,AddBidAmountSerializer,ViewBidSerializer,EditBidSerializer
from rest_framework import status
from rest_framework import generics,mixins
from account.models import Hirer

# Create your views here.

class AddProjectView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddProjectSerializer
    def post(self, request,format=None):
        serializer = AddProjectSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'status': status.HTTP_200_OK,'message':'Project has been Added Successfully','data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}}, status=status.HTTP_400_BAD_REQUEST)


class ViewAllProject(generics.ListAPIView):
    serializer_class = ViewAllProjectSerializer

    def get(self,request,format=None):
        project_data=Project.objects.all().values('id')
        project_list=[]
        for i in project_data:
            proObj=Project.objects.select_related().get(id=i['id'])
            project_list.append({'id':proObj.id,'title':proObj.title,'description':proObj.description,'budget':proObj.budget,'deadline':proObj.deadline,'skills_required':proObj.skills_required,'category':proObj.category,'project_owner_name':proObj.project_owner.first_Name})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':project_list}, status=status.HTTP_200_OK)


class ViewProjectById(GenericAPIView,mixins.RetrieveModelMixin):
    queryset=Project.objects.all()
    serializer_class = ViewAllProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        chk_pro=Project.objects.filter(id=kwargs['pk'])
        a=self.retrieve(self,request,*args,**kwargs)
        if request.user.is_hirer != True or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Hirer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        if chk_pro.exists():
            pro=Project.objects.select_related().get(id=kwargs['pk'])
            if pro.project_owner.id == request.user.id:
                return Response({'status': status.HTTP_200_OK,'message':'Ok','data':a.data}, status=status.HTTP_200_OK)
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'This is not your project','data':{}}, status=status.HTTP_400_BAD_REQUEST)


class ViewHirerSelfProject(generics.ListAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = ViewAllProjectSerializer
    
    def get(Self,request,*args,**kwargs):
        if request.user.type !="HIRER" or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Hirer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        hirerPro=[]
        hirerlist=Project.objects.filter(project_owner_id=request.user.id).values()
        for i in hirerlist:
            hirerPro.append({'id':i['id'],'title':i['title'],'description':i['description'],'budget':i['budget'],'deadline':i['deadline'],'skills_required':i['skills_required'],'category':i['category']})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':hirerPro}, status=status.HTTP_200_OK)


class ProjectUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectUpdateSeralizer
    queryset = Project.objects.all()

    def put(self,request,*args,**kwargs):
        if request.user.type != 'HIRER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Hirer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projectObj = Project.objects.select_related().get(id=kwargs['pk'])
        except Project.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Project Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if projectObj.project_owner.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance=projectObj, data=request.data, context={'projectObj': projectObj, "user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Project updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


class DeleteProjectView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def delete(self,request,*args,**kwargs):
        if request.user.type != 'HIRER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Hirer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projectObj = Project.objects.select_related().get(id=kwargs['pk'])
        except Project.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Project Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if projectObj.project_owner.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        del_project=self.destroy(self,request,*args,**kwargs)
        return Response({'status': status.HTTP_200_OK, 'message': 'Project Deleted Sucessfully', 'data':{str(del_project)}}, status=status.HTTP_200_OK)
        
class AddBidView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBidAmountSerializer
    queryset = Bid.objects.all()

    def post(self, request, *args, **kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Your ID is Blocked or You are not a freelancer', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

        proj_id = kwargs['pk']
        try:
            pro_bid = Project.objects.get(id=proj_id)
        except Project.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Project Not Found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

        existing_bid = Bid.objects.filter(project=pro_bid, freelancer=request.user)
        if existing_bid.exists():
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'You Have Already Placed a Bid On this project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'proj_id': proj_id, 'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'status': status.HTTP_200_OK, 'message': 'Add Bid Amount Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ViewBidById(GenericAPIView,mixins.RetrieveModelMixin):
    # serializer_class = [IsAuthenticated]
    serializer_class = ViewBidSerializer
    queryset = Bid.objects.all()

    def get(self, request, *args, **kwargs):
        project_id = kwargs['pk']
        chk_bid = Bid.objects.filter(project_id=project_id)
        
        # if request.user.Block == True:
        #     return Response({'status':status.HTTP_403_FORBIDDEN,'message':'your profile is Block','data':{}},status=status.HTTP_403_FORBIDDEN)
        
        if chk_bid.exists():
            bids = Bid.objects.filter(project_id=project_id).values('id')
            my_bids=[]
            for i in bids:
                obj_call=Bid.objects.select_related().get(id=i['id'])
                formatted_date = obj_call.bid_time.strftime("%Y-%m-%d %I:%M %p")
                # bid_time_str = obj_call.bid_time.strftime('%Y-%m-%d %H:%M:%S')
                # print(obj_call.bid_time)
                my_bids.append({'id': obj_call.id,'bid_amount': obj_call.bid_amount,'description': obj_call.description,'bid_time':formatted_date,'freelancer_first_Name':obj_call.freelancer.first_Name,'project':obj_call.project.id})
            return Response({'status': status.HTTP_200_OK, 'message': 'OK', 'data': my_bids}, status=status.HTTP_200_OK)
        else:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'No bids found for this project', 'data': {}}, status=status.HTTP_404_NOT_FOUND)


class DeleteBidView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Bid.objects.all()


    def delete(self,request,*args,**kwargs):
        if request.user.type !='FREELANCER' or request.user.Block == True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Freelancer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bid_det = Bid.objects.select_related().get(id=kwargs['pk'])
        except Bid.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Bid Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        if bid_det.freelancer.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your Bid', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        del_bid=self.destroy(self,request,*args,**kwargs)
        return Response({'status': status.HTTP_200_OK, 'message': 'Bid Deleted Sucessfully', 'data':{str(del_bid)}}, status=status.HTTP_200_OK)
    

class BidUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = EditBidSerializer
    queryset = Bid.objects.all()

    def put(self,request,*args,**kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Freelancer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bidobj = Bid.objects.select_related().get(id=kwargs['pk'])
        except Bid.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Bid Id Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        if bidobj.freelancer.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your Bid', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance=bidobj, data=request.data,context={'bidobj':bidobj,'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Bid Edit Sucessfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)