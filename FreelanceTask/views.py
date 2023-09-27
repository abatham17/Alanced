from django.shortcuts import render
from . models import Project,Bid,Membership,Review,FreelancerProject
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import AddProjectSerializer,ViewAllProjectSerializer,ProjectUpdateSeralizer,AddBidAmountSerializer,ViewBidSerializer,EditBidSerializer,ViewAllMembershipSerializer,AddReviewSeralizer,EditReviewSeralizer,FreelancerAddProjectSerializer,FreelancerProjectUpdateSeralizer,ViewAllReviewSerializer,ViewAllFreelancerProjectSerializer
from rest_framework import status
from rest_framework import generics,mixins
from account.models import Hirer,Freelancer
from datetime import datetime

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
            project_list.append({'id':proObj.id,'title':proObj.title,'description':proObj.description,'budget':proObj.budget,'deadline':proObj.deadline,'skills_required':proObj.skills_required,'category':proObj.category,'project_owner_name':proObj.project_owner.first_Name+ " "+ proObj.project_owner.last_Name,'project_creation_date':proObj.created_at,'project_owner_location':proObj.project_owner.Address,'project_owner_contact':proObj.project_owner.contact})
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
            hirerPro.append({'id':i['id'],'title':i['title'],'description':i['description'],'budget':i['budget'],'deadline':i['deadline'],'skills_required':i['skills_required'],'category':i['category'],'Project_created_at':i['created_at']})
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
        
        
        if chk_bid.exists():
            bids = Bid.objects.filter(project_id=project_id).values('id')
            my_bids=[]
            for i in bids:
                obj_call=Bid.objects.select_related().get(id=i['id'])
                formatted_date = obj_call.bid_time.strftime("%Y-%m-%d %I:%M %p")
                print(formatted_date)
                my_bids.append({'id': obj_call.id,'bid_amount': obj_call.bid_amount,'description': obj_call.description,'bid_time':formatted_date,'freelancer_Name':obj_call.freelancer.first_Name+" "+obj_call.freelancer.last_Name,'project_id':obj_call.project.id,'freelancer_category':obj_call.freelancer.category,'freelancer_address':obj_call.freelancer.Address,'Freelancer_skills':obj_call.freelancer.skills,'freelancer_profilepic':'/media/'+str(obj_call.freelancer.images_logo),'freelancer_about':obj_call.freelancer.about,"project":{'title':obj_call.project.title,'description':obj_call.project.description,'category':obj_call.project.category,'skills_required':obj_call.project.skills_required,'deadline':obj_call.project.deadline,'budget':obj_call.project.budget,'created_at':obj_call.project.created_at}})
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
    

class ViewAllHirerMembership(generics.ListAPIView):
    serializer_class = ViewAllMembershipSerializer

    def get(self, request, format=None):
        membership_data = Membership.objects.all().values()
        hirer_list = []

        for i in membership_data:
            membership_item = {
                'name': i['name'],
                'features': i['features'],
                'price': '₹' + str(i['price']),
                'duration': str(i['duration']) + ' days',
                'membership_type': i['membership_type']
            }

            if i['membership_type'].lower() == 'hirer':
                hirer_list.append(membership_item)

        return Response({'status': status.HTTP_200_OK,'message': "Ok",'data': hirer_list }, status=status.HTTP_200_OK)
    

class ViewAllFreelancerMembership(generics.ListAPIView):
    serializer_class = ViewAllMembershipSerializer

    def get(self, request, format=None):
        membership_data = Membership.objects.all().values()
        freelancer_list = []

        for i in membership_data:
            membership_item = {
                'name': i['name'],
                'features': i['features'],
                'price': '₹' + str(i['price']),
                'duration': str(i['duration']) + ' days',
                'membership_type': i['membership_type']
            }

            if i['membership_type'].lower() == 'freelancer':
                freelancer_list.append(membership_item)
         
        return Response({'status': status.HTTP_200_OK,'message': "Ok",'data':freelancer_list}, status=status.HTTP_200_OK)         


class AddReviewsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddReviewSeralizer
    queryset = Review.objects.all()

    def post(self,request,*args,**kwargs):
        if request.user.type != 'HIRER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Hirer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        free_id=kwargs['pk']
        try:
            freelancerObj = Freelancer.objects.get(id=free_id)
        except Freelancer.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        serializer = AddReviewSeralizer(data=request.data, context={'free_id': free_id, "user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Review Added Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class ViewAllReviews(generics.ListAPIView):
    serializer_class = ViewAllReviewSerializer
    queryset = Review.objects.all()

    def get(self,request,*args,**kwargs):
        free_id = self.kwargs['pk']
        print(free_id)
        revdata = Review.objects.filter(created_for_id=free_id)
        if not revdata:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        rev = []
        for rev_list in revdata:
            rev.append({
                'Reviewee': rev_list.created_for.first_Name, 
                'Reviewer': rev_list.created_by.first_Name,
                'rating': rev_list.rating,
                'review': rev_list.review
            })
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': rev}, status=status.HTTP_200_OK)

class EditReviews(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = EditReviewSeralizer
    queryset = Review.objects.all()

    def put(self,request,*args,**kwargs):
        if request.user.type != 'HIRER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Hirer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            revObj = Review.objects.select_related().get(id=kwargs['pk'])
        except Review.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Review Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if revObj.created_by.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your Review', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance=revObj, data=request.data, context={'revObj': revObj, "user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Your Review is updated Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 


class DeleteReviews(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()

    def delete(self,request,*args,**kwargs):
        if request.user.type != 'HIRER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Hirer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            revObj = Review.objects.select_related().get(id=kwargs['pk'])
        except Review.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Review Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if revObj.created_by.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your Review', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        del_project=self.destroy(self,request,*args,**kwargs)
        return Response({'status': status.HTTP_200_OK, 'message': 'Your Review Deleted Sucessfully', 'data':{str(del_project)}}, status=status.HTTP_200_OK)       
    

class FreelancerAddProjectView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=FreelancerAddProjectSerializer
    def post(self, request,format=None):
        serializer = FreelancerAddProjectSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'status': status.HTTP_200_OK,'message':'Project has been Added Successfully','data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}}, status=status.HTTP_400_BAD_REQUEST)


class ViewAllFreelancerProjects(generics.ListAPIView):
    serializer_class = ViewAllFreelancerProjectSerializer
    queryset = FreelancerProject.objects.all()

    def get(self, request, *args, **kwargs):
        free_id = self.kwargs['pk']
        proj_data = FreelancerProject.objects.filter(design_by_id=free_id)
        if not proj_data:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        project_data = []
        for pro_list in proj_data:
            project_data.append({
                'project_title': pro_list.project_title, 
                'project_description': pro_list.project_description,
                'project_link': pro_list.project_link,
                'images_logo': '/media/'+str(pro_list.images_logo),
                'project_pdf': '/media/'+str(pro_list.project_pdf),
                'skills_used':pro_list.skills_used,
                'category':pro_list.category,
                'design_by':pro_list.design_by.first_Name+" "+pro_list.design_by.last_Name,
            })
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': project_data}, status=status.HTTP_200_OK)
    

class FreelancerProjectUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerProjectUpdateSeralizer
    queryset = FreelancerProject.objects.all()

    def put(self,request,*args,**kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Freelancer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projectObj = FreelancerProject.objects.select_related().get(id=kwargs['pk'])
        except FreelancerProject.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Project Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if projectObj.design_by.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance=projectObj, data=request.data, context={'projectObj': projectObj, "user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Project updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    
    

class DeleteFreelancerProjectView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = FreelancerProject.objects.all()

    def delete(self,request,*args,**kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Freelancer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projectObj = FreelancerProject.objects.select_related().get(id=kwargs['pk'])
        except FreelancerProject.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Project Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if projectObj.design_by.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        del_project=self.destroy(self,request,*args,**kwargs)
        return Response({'status': status.HTTP_200_OK, 'message': 'Project Deleted Sucessfully', 'data':{str(del_project)}}, status=status.HTTP_200_OK)  



class ViewFreelancerSelfBid(generics.ListAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = ViewBidSerializer
    
    def get(Self,request,*args,**kwargs):
        if request.user.type !="FREELANCER" or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Freelancer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        freelanceBid=[]
        freelancelist=Bid.objects.filter(freelancer_id=request.user.id).values("id")
        for i in freelancelist:
            bidobj=Bid.objects.select_related().get(id=i['id'])
            print(bidobj,"bid")
            freelanceBid.append({'id':bidobj.id,'bid_amount':bidobj.bid_amount,'description':bidobj.description,'bid_time':bidobj.bid_time,'freelancer_id':bidobj.freelancer_id,'project_id':bidobj.project_id,"project":{'title':bidobj.project.title,'category':bidobj.project.category,'description':bidobj.project.description,'skills_required':bidobj.project.skills_required,'budget':bidobj.project.budget,'deadline':bidobj.project.deadline,'created_at':bidobj.project.created_at}})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':freelanceBid}, status=status.HTTP_200_OK)


class ViewFreelancerSelfProjectBid(generics.ListAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = ViewBidSerializer
    
    def get(Self,request,*args,**kwargs):
        project_id = kwargs['pk']
        if request.user.type !="FREELANCER" or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Freelancer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        freelanceProjectBid=[]
        freelanceProjectlist=Bid.objects.filter(freelancer_id=request.user.id,project_id=project_id).values("id")
        for i in freelanceProjectlist:
            probidobj=Bid.objects.select_related().get(id=i['id'])
            print(probidobj,"bid")
            freelanceProjectBid.append({'id':probidobj.id,'bid_amount':probidobj.bid_amount,'description':probidobj.description,'bid_time':probidobj.bid_time,'freelancer_id':probidobj.freelancer_id,'project_id':probidobj.project_id,"project":{'title':probidobj.project.title,'category':probidobj.project.category,'description':probidobj.project.description,'skills_required':probidobj.project.skills_required,'budget':probidobj.project.budget,'deadline':probidobj.project.deadline,'created_at':probidobj.project.created_at}})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':freelanceProjectBid}, status=status.HTTP_200_OK)  


