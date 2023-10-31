from django.shortcuts import render
from . models import Project,Bid,Membership,Review,FreelancerProject,SavedProject,FreelancerEmployment,Subscription,UserContactUs
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import AddProjectSerializer,ViewAllProjectSerializer,ProjectUpdateSeralizer,AddBidAmountSerializer,ViewBidSerializer,EditBidSerializer,ViewAllMembershipSerializer,AddReviewSeralizer,EditReviewSeralizer,FreelancerAddProjectSerializer,FreelancerProjectUpdateSeralizer,ViewAllReviewSerializer,ViewAllFreelancerProjectSerializer,FreelancerEmploymentUpdateSeralizer,FreelancerAddEmploymentSerializer,SubscriptionSerializer,UserContantUsSerializer
from rest_framework import status
from rest_framework import generics,mixins
from account.models import Hirer,Freelancer
from datetime import datetime
from django.db.models import Q
from rest_framework import filters, viewsets

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

    def get(self, request, format=None):
        # Start with the base queryset
        queryset = Project.objects.all()

        # Define filters based on query parameters
        category_filter = request.query_params.getlist('category')
        address_filter = request.query_params.getlist('project_owner_location')
        experience_filter = request.query_params.getlist('experience_level')
        # skills_filter = request.GET.get('skills_required')
        rate_filter = request.query_params.getlist('rate')
        skills_param = request.query_params.getlist('skills_required')
        min_hourly_rate_filter = request.query_params.get('min_hourly_rate')
        max_hourly_rate_filter = request.query_params.get('max_hourly_rate')

        # Search filter based on all fields
        search_query = request.query_params.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(rate__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(experience_level__icontains=search_query) |
                Q(skills_required__icontains=search_query) |
                Q(project_owner__first_Name__icontains=search_query) |
                Q(project_owner__Address__icontains=search_query) |
                Q(project_owner__contact__icontains=search_query)
            )


        if category_filter:
            category_filter_q = Q()
            for category in category_filter:
                category_filter_q |= Q(category=category)
            queryset = queryset.filter(category_filter_q)

        if address_filter:
            address_filter_q = Q()
            for address in address_filter:
                address_filter_q |= Q(project_owner__Address=address)
            queryset = queryset.filter(address_filter_q)

        if experience_filter:
            experience_filter_q = Q()
            for experience in experience_filter:
                experience_filter_q |= Q(experience_level=experience)
            queryset = queryset.filter(experience_filter_q)

        if rate_filter:
            rate_filter_q = Q()
            for rate in rate_filter:
                rate_filter_q |= Q(rate=rate)
            queryset = queryset.filter(rate_filter_q)

        # Filter based on min_hourly_rate and max_hourly_rate
        if min_hourly_rate_filter:
            queryset = queryset.filter(min_hourly_rate__gte=min_hourly_rate_filter)
        if max_hourly_rate_filter:
            queryset = queryset.filter(max_hourly_rate__lte=max_hourly_rate_filter)

            
        if skills_param:
            skill_filter_q = Q()
            for skills in skills_param:
                skill_filter_q |= Q(skills_required__contains=skills)
            queryset = queryset.filter(skill_filter_q)

       
        project_list = []
        for proObj in queryset:
            project_list.append({
                'id': proObj.id,
                'title': proObj.title,
                'description': proObj.description,
                'rate': proObj.rate,
                'fixed_budget': proObj.fixed_budget,
                'min_hourly_rate': proObj.min_hourly_rate,
                'max_hourly_rate': proObj.max_hourly_rate,
                'deadline': proObj.deadline,
                'skills_required': proObj.skills_required,
                'category': proObj.category,
                'project_owner_name': proObj.project_owner.first_Name,
                'project_creation_date': proObj.created_at,
                'project_owner_location': proObj.project_owner.Address,
                'project_owner_contact': proObj.project_owner.contact,
                'experience_level': proObj.experience_level,
            })

        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': project_list}, status=status.HTTP_200_OK)
    

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
    queryset = Project.objects.all()
    
    def get(self, request, *args, **kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message':'Your Profile is Blocked or Not a Hirer Profile', 'data':{}}, status=status.HTTP_403_FORBIDDEN)
        
        hirerPro = []
        hirer_projects = Project.objects.filter(project_owner_id=request.user.id)
        
        for project in hirer_projects:
            hirerPro.append({
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'Project_Rate': project.rate,
                'Project_Fixed_Budget': project.fixed_budget,
                'Project_Min_Hourly_Rate': project.min_hourly_rate,
                'Project_Max_Hourly_Rate': project.max_hourly_rate,
                'deadline': project.deadline,
                'skills_required': project.skills_required,
                'category': project.category,
                'Project_created_at': project.created_at,
                'project_owner_id': project.project_owner.id,
                'project_owner_address': project.project_owner.Address,
                'project_owner_created': project.project_owner.date_of_creation
            })
        
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': hirerPro}, status=status.HTTP_200_OK)


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
                my_bids.append({'id': obj_call.id,'bid_amount': obj_call.bid_amount,'description': obj_call.description,'bid_type':obj_call.bid_type,'bid_time':formatted_date,'freelancer_Name':obj_call.freelancer.first_Name+" "+obj_call.freelancer.last_Name,'project_id':obj_call.project.id,'freelancer_category':obj_call.freelancer.category,'freelancer_address':obj_call.freelancer.Address,'Freelancer_skills':obj_call.freelancer.skills,'freelancer_profilepic':'/media/'+str(obj_call.freelancer.images_logo),'freelancer_about':obj_call.freelancer.about,"project":{'title':obj_call.project.title,'description':obj_call.project.description,'category':obj_call.project.category,'skills_required':obj_call.project.skills_required,'deadline':obj_call.project.deadline,'fixed_budget':obj_call.project.fixed_budget,'rate':obj_call.project.rate,'min_hourly_rate':obj_call.project.min_hourly_rate,'max_hourly_rate':obj_call.project.max_hourly_rate, 'created_at':obj_call.project.created_at}})
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
    queryset = Membership.objects.all()

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
    queryset = Membership.objects.all()

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

    def post(self, request, *args, **kwargs):
        if request.user.type != 'HIRER' or request.user.Block == True:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Your Id is Blocked or You are not a Hirer', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        
        free_id = kwargs['pk']
        try:
            freelancerObj = Freelancer.objects.get(id=free_id)
        except Freelancer.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Profile Not Found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

        projects_id = request.data.get('projects')
        if not projects_id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'project_id is required in the request body', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(id=projects_id)
        except Project.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Project Not Found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        
        if project.project_owner != request.user:
           return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'You are not the owner of this project', 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddReviewSeralizer(data=request.data, context={'free_id': free_id, "user": request.user, "project": project})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Review Added Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    

class ViewAllReviews(generics.ListAPIView):
    
    serializer_class = ViewAllReviewSerializer
    queryset = Review.objects.all()


    def get(self, request, *args, **kwargs):
        free_id = self.kwargs['pk']
        revdata = Review.objects.filter(created_for_id=free_id)
        if not revdata:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        rev = []
        for rev_list in revdata:
            rev.append({
                'Reviewee': rev_list.created_for.first_Name, 
                'Reviewer': rev_list.created_by.first_Name,
                'rating': rev_list.rating,
                'review': rev_list.review,
                'Project_Name':rev_list.projects.title,
                'project_Rate':rev_list.projects.rate,
                'project_Budget':rev_list.projects.fixed_budget,
                'project_Min_Hourly_Rate':rev_list.projects.min_hourly_rate,
                'project_Max_Hourly_Rate':rev_list.projects.max_hourly_rate,
                'project_deadline':rev_list.projects.deadline,
                'reviews_created_date':rev_list.created_at
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
    queryset = FreelancerProject.objects.all()
    serializer_class = ViewAllFreelancerProjectSerializer
    def get(self, request, *args, **kwargs):
        free_id = self.kwargs['pk']
        proj_data = FreelancerProject.objects.filter(design_by_id=free_id)
        if not proj_data:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        project_data = []
        for pro_list in proj_data:
            project_data.append({
                'project_id':pro_list.id,
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
    queryset = Bid.objects.all()
    
    def get(Self,request,*args,**kwargs):
        if request.user.type !="FREELANCER" or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Freelancer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        freelanceBid=[]
        freelancelist=Bid.objects.filter(freelancer_id=request.user.id).values("id")
        for i in freelancelist:
            bidobj=Bid.objects.select_related().get(id=i['id'])
            print(bidobj,"bid")
            freelanceBid.append({'id':bidobj.id,'bid_amount':bidobj.bid_amount,'description':bidobj.description,'bid_type':bidobj.bid_type,'bid_time':bidobj.bid_time,'freelancer_id':bidobj.freelancer_id,'project_id':bidobj.project_id,"project":{'title':bidobj.project.title,'category':bidobj.project.category,'description':bidobj.project.description,'skills_required':bidobj.project.skills_required,'Project_rate':bidobj.project.rate,'Project_budget':bidobj.project.fixed_budget,'Project_min_hourly_rate':bidobj.project.min_hourly_rate,'Project_max_hourly_rate':bidobj.project.max_hourly_rate,'Project_experience_level':bidobj.project.experience_level,'deadline':bidobj.project.deadline,'created_at':bidobj.project.created_at}})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':freelanceBid}, status=status.HTTP_200_OK)


class ViewFreelancerSelfProjectBid(generics.ListAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = ViewBidSerializer
    queryset = Bid.objects.all()
    
    def get(Self,request,*args,**kwargs):
        project_id = kwargs['pk']
        if request.user.type !="FREELANCER" or request.user.Block == True:
            return Response ({'status': status.HTTP_403_FORBIDDEN,'message':'Your Profile is Blocked or Not a Freelancer Profile','data':{}}, status=status.HTTP_403_FORBIDDEN)
        freelanceProjectBid=[]
        freelanceProjectlist=Bid.objects.filter(freelancer_id=request.user.id,project_id=project_id).values("id")
        for i in freelanceProjectlist:
            probidobj=Bid.objects.select_related().get(id=i['id'])
            print(probidobj,"bid")
            freelanceProjectBid.append({'id':probidobj.id,'bid_amount':probidobj.bid_amount,'description':probidobj.description,'bid_type':probidobj.bid_type,'bid_time':probidobj.bid_time,'freelancer_id':probidobj.freelancer_id,'project_id':probidobj.project_id,"project":{'title':probidobj.project.title,'category':probidobj.project.category,'description':probidobj.project.description,'skills_required':probidobj.project.skills_required,'deadline':probidobj.project.deadline,'fixed_budget':probidobj.project.fixed_budget,'rate':probidobj.project.rate,'min_hourly_rate':probidobj.project.min_hourly_rate,'max_hourly_rate':probidobj.project.max_hourly_rate,'experience_level':probidobj.project.experience_level,'created_at':probidobj.project.created_at}})
        return Response({'status': status.HTTP_200_OK,'message':'Ok','data':freelanceProjectBid}, status=status.HTTP_200_OK)  


class SavedProjectsView(generics.CreateAPIView):
    queryset = SavedProject.objects.all()

    def post(self, request, *args, **kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'Your Id is Blocked or You are not a Freelancer'}, status=status.HTTP_403_FORBIDDEN)
        
        project_id = kwargs['pk']
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        saved_project, created = SavedProject.objects.get_or_create(
            freelancer=request.user,
            project=project
        )

        if not created:
            saved_project.delete()
            return Response({'status': status.HTTP_200_OK, 'message': 'Project unsaved', 'isSaved': False}, status=status.HTTP_200_OK)

        return Response({'status': status.HTTP_201_CREATED, 'message': 'Project saved', 'isSaved': True}, status=status.HTTP_201_CREATED)
    


class ViewAllSavedJobs(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SavedProject.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            freelancer = request.user
        except AttributeError:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)

        saveddata = SavedProject.objects.filter(freelancer_id=freelancer)
        
        if not saveddata.exists():
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'No saved jobs found','data':{}}, status=status.HTTP_404_NOT_FOUND)

        res = []
        for save_list in saveddata:
            res.append({
                'Project_id': save_list.project.id,
                'Project_Name': save_list.project.title ,
                'Project_Description': save_list.project.description,
                'deadline': save_list.project.deadline,
                'Project_Rate': save_list.project.rate,
                'Project_Fixed_Budget': save_list.project.fixed_budget,
                'Project_Min_Hourly_Rate': save_list.project.min_hourly_rate,
                'Project_Max_Hourly_Rate': save_list.project.max_hourly_rate,
                'Project_skills':save_list.project.skills_required,
                'Project_Created':save_list.project.created_at,
                'Project_Experience_level': save_list.project.experience_level,
                'Project_Hirer_Location': save_list.project.project_owner.Address
            })

        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': res}, status=status.HTTP_200_OK)
    

class FreelancerEmploymentUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerEmploymentUpdateSeralizer
    queryset = FreelancerEmployment.objects.all()

    def put(self,request,*args,**kwargs):
        if request.user.type != 'FREELANCER' or request.user.Block==True:
            return Response({'status': status.HTTP_400_BAD_REQUEST,'message':'Your Id is Block or You are not a Freelancer','data':{}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            empObj = FreelancerEmployment.objects.select_related().get(id=kwargs['pk'])
        except FreelancerEmployment.DoesNotExist:
             return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Data Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)  
        if empObj.add_by.id != request.user.id:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'This is not your employment data', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance=empObj, data=request.data, context={'empObj': empObj, "user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'Employment Data updated', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid data', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class FreelancerAddEmploymentView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=FreelancerAddEmploymentSerializer
    def post(self, request,format=None):
        serializer = FreelancerAddEmploymentSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'status': status.HTTP_200_OK,'message':'Employment Data Added Successfully','data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}}, status=status.HTTP_400_BAD_REQUEST)
    
class ViewAllFreelancerEmployment(generics.ListAPIView):
    queryset= FreelancerEmployment.objects.all()
    serializer_class=FreelancerAddEmploymentSerializer
    def get(self, request, *args, **kwargs):
        free_id = self.kwargs['pk']
        emp_data = FreelancerEmployment.objects.filter(add_by_id=free_id)
        if not emp_data:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'Profile Not Found','data':{}}, status=status.HTTP_404_NOT_FOUND)
        employment_data = []
        for emp_list in emp_data:
            employment_data.append({
                'emp_id':emp_list.id,
                'Freelancer_Company_Name':emp_list.Freelancer_Company_Name,
                'Company_Designation':emp_list.Company_Designation,
                'Company_Joining_date':emp_list.Company_Joining_date,
                'Company_Leaving_date':emp_list.Company_Leaving_date,
                'design_by':emp_list.add_by.first_Name+" "+emp_list.add_by.last_Name,
            })
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': employment_data}, status=status.HTTP_200_OK)
    

class SubscriptionView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status': status.HTTP_201_CREATED,'message': ' Thankyou for Subscribe!','data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message': serializer.errors,'data': {}}, status=status.HTTP_400_BAD_REQUEST)
    

class UserContactUsView(generics.CreateAPIView):
    queryset = UserContactUs.objects.all()
    serializer_class = UserContantUsSerializer

    def post(self, request):
        serializer = UserContantUsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status':status.HTTP_201_CREATED,'message':'Your data has been Submitted','data':serializer.data},status=status.HTTP_201_CREATED)
        return Response({'status':status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}},status=status.HTTP_400_BAD_REQUEST)