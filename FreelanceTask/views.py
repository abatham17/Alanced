from django.shortcuts import render
from . models import Project,Bid,Membership,Review,FreelancerProject,SavedProject,FreelancerEmployment,Subscription,UserContactUs,ClientNotification,FreelancerNotification, Hire
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from.serializers import AddProjectSerializer,ViewAllProjectSerializer,ProjectUpdateSeralizer,AddBidAmountSerializer,ViewBidSerializer,EditBidSerializer,ViewAllMembershipSerializer,AddReviewSeralizer,EditReviewSeralizer,FreelancerAddProjectSerializer,FreelancerProjectUpdateSeralizer,ViewAllReviewSerializer,ViewAllFreelancerProjectSerializer,FreelancerEmploymentUpdateSeralizer,FreelancerAddEmploymentSerializer,SubscriptionSerializer,UserContantUsSerializer,ClientNotificationSerializer,FreelancerNotificationSerializer,HireSerializer
from rest_framework import status
from rest_framework import generics,mixins
from account.models import Hirer,Freelancer
from datetime import datetime
from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from smtputils import Util
from rest_framework.parsers import MultiPartParser,FormParser
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
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Start with the base queryset
        queryset = Project.objects.all()
        request = self.request

        # Define filters based on query parameters
        category_filter = request.query_params.getlist('category')
        address_filter = request.query_params.getlist('project_owner_location')
        experience_filter = request.query_params.getlist('experience_level')
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

        return queryset
    
    def list(self,request,*args,**kwargs):
        queryset = self.filter_queryset(self.get_queryset())
       
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
                'project_owner_name': proObj.project_owner.first_Name+" "+proObj.project_owner.last_Name,
                'project_creation_date': proObj.created_at,
                'project_owner_location': proObj.project_owner.Address,
                'project_owner_contact': proObj.project_owner.contact,
                'experience_level': proObj.experience_level,
                'is_hired':proObj.is_hired,
                'project_owner_date_of_creation':proObj.project_owner.date_of_creation,
                'project_owner':proObj.project_owner_id
            })

        page = self.paginate_queryset(project_list)
        if page is not None:
            return self.get_paginated_response(page)
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
    pagination_class =PageNumberPagination
    
    def get_queryset(self):
        queryset=Project.objects.filter(project_owner_id=self.request.user.id)
        return queryset
    
    def list(self,request,*args,**kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message':'Your Profile is Blocked or Not a Hirer Profile', 'data':{}}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.filter_queryset(self.get_queryset())

        # Apply search filter
        search_query = self.request.query_params.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(rate__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(experience_level__icontains=search_query) |
                Q(skills_required__icontains=search_query)
            )

        # Check if queryset exists after applying the search filter
        if not queryset.exists():
            return Response({'status': status.HTTP_200_OK, 'message': 'No results found', 'data': []}, status=status.HTTP_200_OK)
        
        hirerPro = []
        # hirer_projects = Project.objects.filter(project_owner_id=request.user.id)
        
        for project in queryset:
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
                'project_owner_created': project.project_owner.date_of_creation,
                'experience_level': project.experience_level,
                'is_hired':project.is_hired,
                'project_owner_name':project.project_owner.first_Name+" "+project.project_owner.last_Name
            })

        page = self.paginate_queryset(hirerPro)
        if page is not None:
            return self.get_paginated_response(page)
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': hirerPro}, status=status.HTTP_200_OK)


#View All Hirer self project api without pagination

class ViewAllHirerSelfProject(generics.ListAPIView):
    permission_classes =[IsAuthenticated]
    serializer_class = ViewAllProjectSerializer
    
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
                'project_owner_created': project.project_owner.date_of_creation,
                'is_hired':project.is_hired,
                'project_owner_name':project.project_owner.first_Name+" "+project.project_owner.last_Name
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

        hireremail = pro_bid.project_owner.email
        data = {
            'email_subject': "New Proposal Received",
            'body': '''
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                .container {
                    background-color: #F2F2F2;
                    margin: 0 auto;
                    padding:50px 130px;
                } 
                .header {
                    background-color:white;
                    padding: 15px 30px;
                }
            </style>
            </head>
            <body>
            <div class="container">
                <div class="header">
                    <h1 style="color: green;letter-spacing: 2px;font-size:22px;">ALANCED</h1>
                    <h3>Congrats! You have Received A New Proposal!!</h3>
                    <p style="font-size:15px">Hi Client, On Your Project You Have Received A New Proposal.</p>
                    <a href="http://localhost:3000/" type="button" style="border: none;color: white;padding: 10px 20px;text-align: center;text-decoration: none;display: inline-block;font-size: 16px;margin: 4px 2px;cursor:pointer;background-color: #4CAF50;border-radius:5px;"><b>View Proposal</b></a>
                    <h3>Thank You, <br>Team Alanced.</h3>
                </div>
            </div>
            </body>
            </html>
            ''',
            'to_email': hireremail
        }

        Util.send_email(data)


        # Notify the project's owner about the new bid
        ClientNotification.objects.create(
            hirer=pro_bid.project_owner,
            title="New Bid Received",
            message=f"{request.user.first_Name} {request.user.last_Name} has placed a bid on your project {pro_bid.title}.",
            type='bid'
        )

        return Response({'status': status.HTTP_200_OK, 'message': 'Add Bid Amount Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ViewBidById(generics.ListAPIView):
    # serializer_class = [IsAuthenticated]
    serializer_class = ViewBidSerializer
    # queryset = Bid.objects.all()
    pagination_class= PageNumberPagination

    def get_queryset(self):
        project_id = self.kwargs['pk']
        chk_bid = Bid.objects.filter(project_id=project_id)
        
        
        if chk_bid.exists():
            bids = Bid.objects.filter(project_id=project_id)
            return bids
        else:
            return Bid.objects.none()
        
    def list(self,request,*args,**kwargs):
            queryset=self.filter_queryset(self.get_queryset())
            search_query = self.request.query_params.get('search_query')
            if search_query:
                queryset = queryset.filter(
                    Q(bid_amount__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(bid_type__icontains=search_query) |
                    Q(freelancer__Address__icontains=search_query) |
                    Q(freelancer__skills__icontains=search_query) |
                    Q(freelancer__first_Name__icontains=search_query) |
                    Q(freelancer__last_Name__icontains=search_query) |
                    Q(freelancer__category__icontains=search_query)
                )


            # if not queryset.exists():
            #     return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'No bids found for this project', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
            if not queryset.exists():
                return Response({'status': status.HTTP_200_OK, 'message': 'No results found', 'data': []}, status=status.HTTP_200_OK)
            my_bids=[]
            for bid in queryset:
                formatted_date = bid.bid_time.strftime("%Y-%m-%d %I:%M %p")
                my_bids.append({
                    'id': bid.id,
                    'bid_amount': bid.bid_amount,
                    'description': bid.description,
                    'bid_type': bid.bid_type,
                    'bid_time': formatted_date,
                    'freelancer_name': f"{bid.freelancer.first_Name} {bid.freelancer.last_Name}",
                    'project_id': bid.project.id,
                    'freelancer_id':bid.freelancer.id,
                    'freelancer_category': bid.freelancer.category,
                    'freelancer_address': bid.freelancer.Address,
                    'freelancer_skills': bid.freelancer.skills,
                    'freelancer_profilepic': '/media/' + str(bid.freelancer.images_logo),
                    'freelancer_about': bid.freelancer.about,
                    'freelancer_hourly_rate':bid.freelancer.hourly_rate,
                    'freelancer_experience_level':bid.freelancer.experience_level,
                    'Freelancer_Languages': bid.freelancer.Language,
                    'Freelancer_qualification':bid.freelancer.qualification,
                    "project": {
                        'title': bid.project.title,
                        'description': bid.project.description,
                        'category': bid.project.category,
                        'skills_required': bid.project.skills_required,
                        'deadline': bid.project.deadline,
                        'fixed_budget': bid.project.fixed_budget,
                        'rate': bid.project.rate,
                        'min_hourly_rate': bid.project.min_hourly_rate,
                        'max_hourly_rate': bid.project.max_hourly_rate,
                        'created_at': bid.project.created_at,
                         'is_hired':bid.project.is_hired
                    }
                })

            # Apply pagination on the manually constructed my_bids
            page = self.paginate_queryset(my_bids)

            if page is not None:
                return self.get_paginated_response(page)


            return Response({'status': status.HTTP_200_OK, 'message': 'OK', 'data': my_bids}, status=status.HTTP_200_OK)


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

    def post(self, request, *args, **kwargs):
        if request.user.type != 'HIRER' or request.user.Block == True:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Your Id is Blocked or You are not a Hirer', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        
        free_id = kwargs['pk']
        try:
            freelancerObj = Freelancer.objects.get(id=free_id)
            print(freelancerObj.email)
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
            freelanceremail = freelancerObj.email
            data = {
                'email_subject': "New Review Received",
                'body': '''
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    .container {
                        background-color: #F2F2F2;
                        margin: 0 auto;
                        padding:50px 130px;
                    } 
                    .header {
                        background-color:white;
                        padding: 15px 30px;
                    }
                </style>
                </head>
                <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: green;letter-spacing: 2px;font-size:22px;">ALANCED</h1>
                        <h3>Congrats! You have Received A New Review!!</h3>
                        <p style="font-size:15px">Hi Freelancer, On Your Project You Have Received A New Review.</p>
                        <a href="http://localhost:3000/" type="button" style="border: none;color: white;padding: 10px 20px;text-align: center;text-decoration: none;display: inline-block;font-size: 16px;margin: 4px 2px;cursor:pointer;background-color: #4CAF50;border-radius:5px;"><b>View Review</b></a>
                        <h3>Thank You, <br>Team Alanced.</h3>
                    </div>
                </div>
                </body>
                </html>
                ''',
                'to_email': freelanceremail
            }

            Util.send_email(data)
            FreelancerNotification.objects.create(
            freelancer=freelancerObj, 
            title="New Review Received", 
            message=f"{request.user.first_Name} {request.user.last_Name} has been added a review for you on project {project.title}.",
            type='review'
            )
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
    parser_classes = [MultiPartParser, FormParser]
    permission_classes=[IsAuthenticated]
    serializer_class=FreelancerAddProjectSerializer
    def post(self, request,format=None):
        serializer = FreelancerAddProjectSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'status': status.HTTP_200_OK,'message':'Project has been Added Successfully','data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}}, status=status.HTTP_400_BAD_REQUEST)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 6     

class ViewAllFreelancerProjects(generics.ListAPIView):
    pagination_class=CustomPageNumberPagination
    def get_queryset(self):
        free_id = self.kwargs['pk']
        proj_data = FreelancerProject.objects.filter(design_by_id=free_id)

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
        return project_data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination on the queryset
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            return self.get_paginated_response(page)

        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': queryset}, status=status.HTTP_200_OK)
    

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
    permission_classes = [IsAuthenticated]
    serializer_class = ViewBidSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        freelancelist = Bid.objects.filter(freelancer_id=self.request.user.id).values("id")
        freelanceBid = []

        for i in freelancelist:
            bidobj = Bid.objects.select_related().get(id=i['id'])
            freelanceBid.append({
                'id': bidobj.id,
                'bid_amount': bidobj.bid_amount,
                'description': bidobj.description,
                'bid_type': bidobj.bid_type,
                'bid_time': bidobj.bid_time,
                'freelancer_id': bidobj.freelancer_id,
                'project_id': bidobj.project_id,
                "project": {
                    'title': bidobj.project.title,
                    'category': bidobj.project.category,
                    'description': bidobj.project.description,
                    'skills_required': bidobj.project.skills_required,
                    'Project_rate': bidobj.project.rate,
                    'Project_budget': bidobj.project.fixed_budget,
                    'Project_min_hourly_rate': bidobj.project.min_hourly_rate,
                    'Project_max_hourly_rate': bidobj.project.max_hourly_rate,
                    'Project_experience_level': bidobj.project.experience_level,
                    'deadline': bidobj.project.deadline,
                    'created_at': bidobj.project.created_at,
                    'project_owner_Name':bidobj.project.project_owner.first_Name,
                    'project_owner_location':bidobj.project.project_owner.Address,
                    'project_owner_date_of_creation':bidobj.project.project_owner.date_of_creation
                }
            })
        return freelanceBid

    def list(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'Your Profile is Blocked or Not a Freelancer Profile', 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        # Fetch the list of bids for the current freelancer
        

        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination on the queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)


        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': queryset}, status=status.HTTP_200_OK)
    

#Freelancer self bid function for get all data 

class ViewFreelancerAllSelfBid(generics.ListAPIView):
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
            freelanceBid.append({'id':bidobj.id,'bid_amount':bidobj.bid_amount,'description':bidobj.description,'bid_type':bidobj.bid_type,'bid_time':bidobj.bid_time,'freelancer_id':bidobj.freelancer_id,'project_id':bidobj.project_id,"project":{'title':bidobj.project.title,'category':bidobj.project.category,'description':bidobj.project.description,'skills_required':bidobj.project.skills_required,'Project_rate':bidobj.project.rate,'Project_budget':bidobj.project.fixed_budget,'Project_min_hourly_rate':bidobj.project.min_hourly_rate,'Project_max_hourly_rate':bidobj.project.max_hourly_rate,'Project_experience_level':bidobj.project.experience_level,'deadline':bidobj.project.deadline,'created_at':bidobj.project.created_at,'project_owner_first_Name':bidobj.project.project_owner.first_Name,'project_owner_address':bidobj.project.project_owner.Address,'project_owner_data_of_creation':bidobj.project.project_owner.date_of_creation}})
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
            freelanceProjectBid.append({'id':probidobj.id,'bid_amount':probidobj.bid_amount,'description':probidobj.description,'bid_type':probidobj.bid_type,'bid_time':probidobj.bid_time,'freelancer_id':probidobj.freelancer_id,'project_id':probidobj.project_id,"project":{'title':probidobj.project.title,'category':probidobj.project.category,'description':probidobj.project.description,'skills_required':probidobj.project.skills_required,'deadline':probidobj.project.deadline,'fixed_budget':probidobj.project.fixed_budget,'rate':probidobj.project.rate,'min_hourly_rate':probidobj.project.min_hourly_rate,'max_hourly_rate':probidobj.project.max_hourly_rate,'experience_level':probidobj.project.experience_level,'created_at':probidobj.project.created_at,'project_owner_Name':probidobj.project.project_owner.first_Name,'project_owner_date_of_creation':probidobj.project.project_owner.date_of_creation,'project_owner_location':probidobj.project.project_owner.Address}})
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
    pagination_class = PageNumberPagination

    def get_queryset(self):
        freelancer=self.request.user
        saveddata = SavedProject.objects.filter(freelancer_id=freelancer)

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
                'Project_Hirer_Location': save_list.project.project_owner.Address,
                'is_hired':save_list.project.is_hired
            })
        return res
    
    def list(self,request,*args,**kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'Your Profile is Blocked or Not a Freelancer Profile', 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination on the queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': queryset}, status=status.HTTP_200_OK)
    

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
            return Response({'status': status.HTTP_200_OK,'message': ' Thankyou for Subscribe!','data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': status.HTTP_400_BAD_REQUEST,'message': serializer.errors,'data': {}}, status=status.HTTP_400_BAD_REQUEST)
    

class UserContactUsView(generics.CreateAPIView):
    queryset = UserContactUs.objects.all()
    serializer_class = UserContantUsSerializer

    def post(self, request):
        serializer = UserContantUsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'message':'Your data has been Submitted','data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST,'message':serializer.errors,'data':{}},status=status.HTTP_400_BAD_REQUEST)
    

class ClientNotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientNotificationSerializer
    queryset = ClientNotification.objects.all()


    def get(self,request,*args,**kwargs):
        if request.user.type!="HIRER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Hirer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        # Assuming the authenticated user is the Hirer
        notdata = ClientNotification.objects.filter(hirer=self.request.user).order_by('-timestamp')
        serializer = ClientNotificationSerializer(notdata, many=True)
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ClientNotificationUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientNotificationSerializer
    queryset = ClientNotification.objects.all()

    def put(self, request, *args, **kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status':status.HTTP_403_FORBIDDEN, 'message':"You're not a Hirer profile or your id is block", 'data':{}}, status=status.HTTP_403_FORBIDDEN)

        notification_id = self.kwargs.get('pk') 
        try:
            notification = ClientNotification.objects.get(pk=notification_id, hirer=self.request.user)

            notification.is_read = True
            notification.save()

            serializer = ClientNotificationSerializer(notification)
            return Response({'status': status.HTTP_200_OK, 'message': 'Notification marked as read', 'data': serializer.data}, status=status.HTTP_200_OK)

        except ClientNotification.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Notification not found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        

class ClientNotificationDeleteView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientNotificationSerializer
    queryset = ClientNotification.objects.all()
    lookup_field = 'id' 

    def delete(self, request, *args, **kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Hirer profile or your id is block", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        
        notif = self.get_object()

        if notif.hirer != request.user:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You can't delete this notification", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        
        notif.delete()
        return Response({'status': status.HTTP_200_OK, 'message': 'Notification deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
    

class FreelancerNotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerNotificationSerializer
    queryset = FreelancerNotification.objects.all()


    def get(self,request,*args,**kwargs):
        if request.user.type!="FREELANCER" or request.user.Block==True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Freelancer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        notdata = FreelancerNotification.objects.filter(freelancer=self.request.user).order_by('-timestamp')
        serializer = FreelancerNotificationSerializer(notdata, many=True)
        return Response({'status': status.HTTP_200_OK, 'message': 'Ok', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class FreelancerNotificationUpdateView(GenericAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerNotificationSerializer
    queryset = FreelancerNotification.objects.all()

    def put(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status':status.HTTP_403_FORBIDDEN, 'message':"You're not a Freelancer profile or your id is block", 'data':{}}, status=status.HTTP_403_FORBIDDEN)

        notification_id = self.kwargs.get('pk') 
        try:
            notification = FreelancerNotification.objects.get(pk=notification_id, freelancer=self.request.user)

            notification.is_read = True
            notification.save()

            serializer = FreelancerNotificationSerializer(notification)
            return Response({'status': status.HTTP_200_OK, 'message': 'Notification marked as read', 'data': serializer.data}, status=status.HTTP_200_OK)

        except FreelancerNotification.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Notification not found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)


class FreelancerNotificationDeleteView(GenericAPIView,mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = FreelancerNotificationSerializer
    queryset = FreelancerNotification.objects.all()
    lookup_field = 'id' 

    def delete(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is block", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        
        notif = self.get_object()

        if notif.freelancer != request.user:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You can't delete this notification", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        
        notif.delete()
        return Response({'status': status.HTTP_200_OK, 'message': 'Notification deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
    

class HireFreelancerView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Hire.objects.all()
    serializer_class = HireSerializer

    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        freelancer_id = kwargs['pk']

        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status':status.HTTP_403_FORBIDDEN,'message':"You're not a Hirer profile or your id is block",'data':{}},status=status.HTTP_403_FORBIDDEN)
        
        try:
            project = Project.objects.get(id=project_id)
            freelancer = Freelancer.objects.get(id=freelancer_id)
        except Project.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Project not found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Freelancer.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Freelancer not found', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        

        if project.is_hired:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'you Have Already hired A Freelancer For this Project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        
        project_title = request.data.get('project_title')
        hiring_budget = request.data.get('hiring_budget')
        message = request.data.get('message')
        hiring_budget_type = request.data.get('hiring_budget_type')
        
        if project.project_owner != request.user:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You are not the owner of this project", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        # if project.is_hired:
        #     return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'You have already sent a Hiring Request to freelancer for this project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

        existing_hiring_request = Hire.objects.filter(project=project, hired_freelancer=freelancer).first()

        if existing_hiring_request:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'You have already sent a Hiring Request to this freelancer for this project', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)

        hiring = Hire(project=project, hired_freelancer=freelancer,project_title=project_title,
            hiring_budget=hiring_budget,hiring_budget_type=hiring_budget_type,
            message=message)
        hiring.save()

        # project.is_hired = True
        # project.save()

        response_data = {
            'hire_id':hiring.id,
            'project_id': project.id,
            'freelancer_id':freelancer.id,
            'hired_by': project.project_owner.first_Name + " " + project.project_owner.last_Name,
            'hired_freelancer_name': freelancer.first_Name+" "+freelancer.last_Name,
            'project_title': project_title,
            'hiring_budget': hiring_budget,
            'hiring_budget_type': hiring_budget_type,
            'message': message,
            'hired_at': hiring.hired_at
        }
        FreelancerNotification.objects.create(
            freelancer=freelancer, 
            title="New Hiring Request Received", 
            message=f"{request.user.first_Name} {request.user.last_Name} has been Sent you a hiring request For project {project.title}.",
            type='AllHirereq'
        )

        return Response({'status': status.HTTP_200_OK, 'message': 'Hiring Request Sent successfully', 'data': response_data}, status=status.HTTP_200_OK)
    


class FreelancerAcceptProjectView(GenericAPIView, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Hire.objects.all()
    serializer_class = HireSerializer

    def put(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        hiring = self.get_object()
        project = hiring.project

        if hiring.hired_freelancer != request.user:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You are not authorized to accept this project.", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        if hiring.freelancer_accepted:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'You have already accepted this project.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if project.is_hired:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Another freelancer is already hired for this project. You cannot accept the hiring request.'}, status=status.HTTP_400_BAD_REQUEST)

        hiring.freelancer_accepted = True
        hiring.freelancer_rejected = False
        hiring.save()

        project.is_hired = True
        project.save()

        hirer_email = hiring.project.project_owner
        print(hirer_email)
        ClientNotification.objects.create(
            hirer=hirer_email,
            title="Hiring Invitation Accepted",
            message=f"{request.user.first_Name} {request.user.last_Name} has accepted your hiring invitation for project {hiring.project_title}.",
            type='AllInvite'
        )

        return Response({'status': status.HTTP_200_OK, 'message': 'Project accepted successfully'}, status=status.HTTP_200_OK)     
     

class FreelancerRejectProjectView(GenericAPIView, mixins.UpdateModelMixin):
    queryset = Hire.objects.all()
    serializer_class = HireSerializer

    def put(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        hiring = self.get_object()
        project = hiring.project

        if hiring.hired_freelancer != request.user:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You are not authorized to reject this project.", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        
        if hiring.freelancer_rejected:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'You have already rejected this project.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        hiring.freelancer_rejected = True
        hiring.freelancer_accepted = False
        hiring.save()

        # project.is_hired = False
        # project.save()

        hirer_email = hiring.project.project_owner
        print(hirer_email)
        ClientNotification.objects.create(
            hirer=hirer_email,
            title="Hiring Invitation Rejected",
            message=f"{request.user.first_Name} {request.user.last_Name} has rejected your hiring invitation for project {hiring.project_title}.",
            type='AllInvite'
        )

        return Response({'status': status.HTTP_200_OK, 'message': 'You Have Rejected the hiring Request'}, status=status.HTTP_200_OK)
    

class ViewAllHiringRequests(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination 

    def get(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        freelancer = self.request.user

        # Retrieve hiring requests for the authenticated freelancer
        hiring_requests = Hire.objects.filter(hired_freelancer=freelancer)

        # Customize the response data for each hiring request
        response_data = []
        for hiring_request in hiring_requests:
            response_data.append({
                'hire_id': hiring_request.id,
                'project_id': hiring_request.project.id,
                'freelancer_id': hiring_request.hired_freelancer.id,
                'hired_by': f"{hiring_request.project.project_owner.first_Name} {hiring_request.project.project_owner.last_Name}",
                'hired_freelancer_name': f"{hiring_request.hired_freelancer.first_Name} {hiring_request.hired_freelancer.last_Name}",
                'project_title': hiring_request.project_title,
                'project_category':hiring_request.project.category,
                'project_description':hiring_request.project.description,
                'project_exp_level':hiring_request.project.experience_level,
                'project_skills':hiring_request.project.skills_required,
                'project_deadline':hiring_request.project.deadline,
                'hiring_budget': hiring_request.hiring_budget,
                'hiring_budget_type': hiring_request.hiring_budget_type,
                'message': hiring_request.message,
                'hirer_location':hiring_request.project.project_owner.Address,
                'freelancer_accepted':hiring_request.freelancer_accepted,
                'freelancer_rejected':hiring_request.freelancer_rejected,
                'hirer_creation_date':hiring_request.project.project_owner.date_of_creation,
                'Received_time': hiring_request.hired_at,
                'is_hired':hiring_request.project.is_hired
            })

        # Paginate the response data
        page = self.paginate_queryset(response_data)

        if page is not None:
            return self.get_paginated_response(page)


        return Response({'status': status.HTTP_200_OK, 'message': ' All Invitations Retrieved Successfully', 'data': response_data}, status=status.HTTP_200_OK)
    

class ViewAllInvitedFreelancers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HireSerializer
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.type != "HIRER" or user.Block:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Hirer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        queryset = Hire.objects.filter(project__project_owner=user)

        if not queryset.exists():
            return Response({'status': status.HTTP_204_NO_CONTENT, 'message': 'No hired freelancers found', 'data': []}, status=status.HTTP_204_NO_CONTENT)

        data = []
        for hire in queryset:
            response_data = {
                'hire_id': hire.id,
                'project_id': hire.project.id,
                'freelancer_id': hire.hired_freelancer.id,
                'project_title': hire.project_title,
                'project_description': hire.project.description,
                'project_category': hire.project.category,
                'hiring_budget': hire.hiring_budget,
                'hiring_budget_type': hire.hiring_budget_type,
                'message': hire.message,
                'freelancer_name': f"{hire.hired_freelancer.first_Name} {hire.hired_freelancer.last_Name}",
                'freelancer_category': hire.hired_freelancer.category,
                'freelancer_description': hire.hired_freelancer.about,
                'freelancer_skills': hire.hired_freelancer.skills,
                'freelancer_hourly_rate': hire.hired_freelancer.hourly_rate,
                'freelancer_experience_level': hire.hired_freelancer.experience_level,
                'freelancer_language': hire.hired_freelancer.Language,
                'hire_by': f"{hire.project.project_owner.first_Name} {hire.project.project_owner.last_Name}",
                'freelancer_accepted': hire.freelancer_accepted,
                'freelancer_rejected': hire.freelancer_rejected,
                'hired_at': hire.hired_at,
                'is_hired':hire.project.is_hired
            }
            data.append(response_data)

        page = self.paginate_queryset(data)

        if page is not None:
            return self.get_paginated_response(page)


        return Response({'status': status.HTTP_200_OK, 'message': 'All Invited freelancers retrieved successfully', 'data': data}, status=status.HTTP_200_OK)
    

class ViewAllPendingHiringRequests(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination  

    def get(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        freelancer = self.request.user

        # Retrieve hiring requests for the authenticated freelancer
        hiring_requests = Hire.objects.filter(hired_freelancer=freelancer, freelancer_accepted=False, freelancer_rejected=False)

        # Customize the response data for each hiring request
        response_data = []
        for hiring_request in hiring_requests:
            response_data.append({
                'hire_id': hiring_request.id,
                'project_id': hiring_request.project.id,
                'freelancer_id': hiring_request.hired_freelancer.id,
                'hired_by': f"{hiring_request.project.project_owner.first_Name} {hiring_request.project.project_owner.last_Name}",
                'hired_by_id':hiring_request.project.project_owner.id,
                'hired_freelancer_name': f"{hiring_request.hired_freelancer.first_Name} {hiring_request.hired_freelancer.last_Name}",
                'project_title': hiring_request.project_title,
                'project_category':hiring_request.project.category,
                'project_description':hiring_request.project.description,
                'project_exp_level':hiring_request.project.experience_level,
                'project_skills':hiring_request.project.skills_required,
                'project_deadline':hiring_request.project.deadline,
                'hiring_budget': hiring_request.hiring_budget,
                'hiring_budget_type': hiring_request.hiring_budget_type,
                'message': hiring_request.message,
                'freelancer_accepted':hiring_request.freelancer_accepted,
                'freelancer_rejected':hiring_request.freelancer_rejected,
                'hirer_location':hiring_request.project.project_owner.Address,
                'hirer_creation_date':hiring_request.project.project_owner.date_of_creation,
                'Received_time': hiring_request.hired_at,
                'is_hired':hiring_request.project.is_hired
            })

        # Paginate the response data
        page = self.paginate_queryset(response_data)

        if page is not None:
            return self.get_paginated_response(page)



        return Response({'status': status.HTTP_200_OK, 'message': ' All Pending Invitations Retrieved Successfully', 'data': response_data}, status=status.HTTP_200_OK)
    

class ViewAllFreelancerContracts(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        if request.user.type != "FREELANCER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Freelancer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        freelancer = self.request.user

        
        # Retrieve hiring requests for the authenticated freelancer
        contracts = Hire.objects.filter(hired_freelancer=freelancer,freelancer_accepted=True)

        search_query = request.query_params.get('search_query')
        if search_query:
            contracts = contracts.filter(
                Q(project_title__icontains=search_query) |
                Q(hiring_budget__icontains=search_query) |
                Q(hiring_budget_type__icontains=search_query) 
            )

        # Customize the response data for each hiring request
        response_data = []
        for hiring_request in contracts:
            response_data.append({
                'hire_id': hiring_request.id,
                'project_id': hiring_request.project.id,
                'freelancer_id': hiring_request.hired_freelancer.id,
                'hired_by': f"{hiring_request.project.project_owner.first_Name} {hiring_request.project.project_owner.last_Name}",
                'hired_freelancer_name': f"{hiring_request.hired_freelancer.first_Name} {hiring_request.hired_freelancer.last_Name}",
                'project_title': hiring_request.project_title,
                'project_category':hiring_request.project.category,
                'project_deadline':hiring_request.project.deadline,
                'project_description':hiring_request.project.description,
                'project_exp_level':hiring_request.project.experience_level,
                'project_skills':hiring_request.project.skills_required,
                'project_deadline':hiring_request.project.deadline,
                'hiring_budget': hiring_request.hiring_budget,
                'hiring_budget_type': hiring_request.hiring_budget_type,
                'message': hiring_request.message,
                'freelancer_accepted':hiring_request.freelancer_accepted,
                'freelancer_rejected':hiring_request.freelancer_rejected,
                'hirer_location':hiring_request.project.project_owner.Address,
                'hirer_creation_date':hiring_request.project.project_owner.date_of_creation,
                'Received_time': hiring_request.hired_at,
                'is_hired':hiring_request.project.is_hired
            })

        # Paginate the response data
        page = self.paginate_queryset(response_data)

        if page is not None:
            return self.get_paginated_response(page)



        return Response({'status': status.HTTP_200_OK, 'message': ' All Freelancer Contracts Retrieved Successfully', 'data': response_data}, status=status.HTTP_200_OK)
    

class ViewAllHirerContracts(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Hirer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)
        hirer = self.request.user


        # Retrieve hiring requests for the authenticated freelancer
        contracts = Hire.objects.filter(project__project_owner=hirer,freelancer_accepted=True)

        search_query = request.query_params.get('search_query')
        if search_query:
            contracts = contracts.filter(
                Q(project_title__icontains=search_query) |
                Q(hiring_budget__icontains=search_query) |
                Q(hiring_budget_type__icontains=search_query) |
                Q(hired_freelancer__first_Name__icontains=search_query) |
                Q(hired_freelancer__last_Name__icontains=search_query)
            )

        # Customize the response data for each hiring request
        response_data = []
        for hiring_request in contracts:
            response_data.append({
                'hire_id': hiring_request.id,
                'project_id': hiring_request.project.id,
                'freelancer_id': hiring_request.hired_freelancer.id,
                'hired_by': f"{hiring_request.project.project_owner.first_Name} {hiring_request.project.project_owner.last_Name}",
                'hired_freelancer_name': f"{hiring_request.hired_freelancer.first_Name} {hiring_request.hired_freelancer.last_Name}",
                'project_title': hiring_request.project_title,
                'project_category':hiring_request.project.category,
                'project_description':hiring_request.project.description,
                'project_exp_level':hiring_request.project.experience_level,
                'project_skills':hiring_request.project.skills_required,
                'project_deadline':hiring_request.project.deadline,
                'hiring_budget': hiring_request.hiring_budget,
                'hiring_budget_type': hiring_request.hiring_budget_type,
                'message': hiring_request.message,
                'freelancer_accepted':hiring_request.freelancer_accepted,
                'freelancer_rejected':hiring_request.freelancer_rejected,
                'hirer_location':hiring_request.project.project_owner.Address,
                'hirer_creation_date':hiring_request.project.project_owner.date_of_creation,
                'Sent_time': hiring_request.hired_at,
                'is_hired':hiring_request.project.is_hired
            })

        # Paginate the response data
        page = self.paginate_queryset(response_data)

        if page is not None:
            return self.get_paginated_response(page)



        return Response({'status': status.HTTP_200_OK, 'message': ' All Hirer Contracts Retrieved Successfully', 'data': response_data}, status=status.HTTP_200_OK)
    

class ViewInvitedFreelancersForProject(generics.ListAPIView):
    serializer_class = HireSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.type != "HIRER" or request.user.Block == True:
            return Response({'status': status.HTTP_403_FORBIDDEN, 'message': "You're not a Hirer profile or your id is blocked", 'data': {}}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        project_id = kwargs.get('project_id')

        try:
            project = Project.objects.get(id=project_id, project_owner=user)
        except Project.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Project not found or you are not the owner of the project', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

        invited_freelancers_count = Hire.objects.filter(project__project_owner=user, project__id=project_id).count()

        return Response({'status': status.HTTP_200_OK, 'message': f'Invited freelancers count for project {project_id} retrieved successfully', 'data': invited_freelancers_count}, status=status.HTTP_200_OK)