from rest_framework import serializers
from . models import Project,Bid,Membership,Review,FreelancerProject,FreelancerEmployment
from account.models import Freelancer


class AddProjectSerializer(serializers.ModelSerializer):
    skills_required = serializers.ListField(child=serializers.CharField(), required=False) 
    
    class Meta:
        model=Project
        fields=['title','description','fixed_budget','deadline','skills_required','category','rate','min_hourly_rate','max_hourly_rate','experience_level']

    def validate(self, attrs):
        user=self.context.get('user')
        if user.Block==True:
            raise serializers.ValidationError("Your Profile is Blocked")
        elif user.is_hirer!=True:
            raise serializers.ValidationError("You're not a Hirer Profile") 
        return attrs    
    
    def create(self, validated_data):
        user=self.context.get('user')
        return Project.objects.create(title=self.validated_data['title'],description=self.validated_data['description'],fixed_budget=self.validated_data.get('fixed_budget'),deadline=self.validated_data['deadline'],skills_required=self.validated_data['skills_required'],category=self.validated_data['category'],rate=self.validated_data['rate'],min_hourly_rate=self.validated_data.get('min_hourly_rate'),max_hourly_rate=self.validated_data.get('max_hourly_rate'),experience_level=self.validated_data['experience_level'],project_owner=user)
    

class ViewAllProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','title','description','fixed_budget','deadline','skills_required','category','project_owner_id','experience_level','rate','min_hourly_rate','max_hourly_rate']


class ProjectUpdateSeralizer(serializers.ModelSerializer):
    skills_required = serializers.ListField(child=serializers.CharField(), required=False) 

    class Meta:
        model = Project
        fields = ['title', 'description', 'fixed_budget', 'deadline', 'skills_required', 'category','experience_level','rate','min_hourly_rate','max_hourly_rate']



class AddBidAmountSerializer(serializers.ModelSerializer):
    bid_amount = serializers.DecimalField(max_digits=10,decimal_places=2)
    
    class Meta:
        model = Bid
        fields = ['bid_amount','description']
    
    def create(self, validated_data):
        user=self.context.get('user')
        proj_id=self.context.get('proj_id')
        proj=Project.objects.get(id=proj_id)
        return Bid.objects.create(bid_amount=self.validated_data['bid_amount'],description=self.validated_data['description'],freelancer=user,project=proj)

class ViewBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id','bid_amount','description','bid_time','freelancer_id','project_id']


class EditBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['bid_amount','description']


class ViewAllMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['name','features','price','duration','membership_type']


class AddReviewSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'review', 'projects']

    def create(self, validated_data):
        user = self.context.get('user')
        freelancer = Freelancer.objects.get(id=self.context.get('free_id'))
        project = self.context.get('project')  
        return Review.objects.create(rating=validated_data['rating'],review=validated_data['review'],created_by=user,created_for=freelancer,projects=project)      

class ViewAllReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating','review','created_by','created_for']


class EditReviewSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating','review']
  

class ViewAllFreelancerProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerProject
        fields = ['project_title','project_description','project_link','images_logo','project_pdf','category','skills_used']

class FreelancerAddProjectSerializer(serializers.ModelSerializer):
    skills_used = serializers.ListField(child=serializers.CharField(), required=False) 
   
    class Meta:
        model=FreelancerProject
        fields=['project_title','project_description','project_link','images_logo','project_pdf','category','skills_used']

    def validate(self, attrs):
        user=self.context.get('user')
        if user.Block==True:
            raise serializers.ValidationError("Your Profile is Blocked")
        if user.is_freelancer!=True:
            raise serializers.ValidationError("You're not a Freelancer Profile") 
        return attrs    
    
    def create(self, validated_data):
        user=self.context.get('user')
        return FreelancerProject.objects.create(project_title=self.validated_data['project_title'],project_description=self.validated_data['project_description'],project_link=self.validated_data['project_link'],images_logo=validated_data.get('images_logo'),project_pdf=validated_data.get('project_pdf'),category=self.validated_data['category'],skills_used=self.validated_data['skills_used'],design_by=user) 
    

class FreelancerProjectUpdateSeralizer(serializers.ModelSerializer):
    skills_used=serializers.ListField(child=serializers.CharField())
    class Meta:
        model = FreelancerProject
        fields = ['project_title','project_description','project_link','images_logo','project_pdf','category','skills_used']  


class FreelancerAddEmploymentSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=FreelancerEmployment
        fields=['Freelancer_Company_Name','Company_Designation','Company_Joining_date','Company_Leaving_date']

    def validate(self, attrs):
        user=self.context.get('user')
        if user.Block==True:
            raise serializers.ValidationError("Your Profile is Blocked")
        if user.is_freelancer!=True:
            raise serializers.ValidationError("You're not a Freelancer Profile") 
        return attrs    
    
    def create(self, validated_data):
        user=self.context.get('user')
        return FreelancerEmployment.objects.create(Freelancer_Company_Name=self.validated_data['Freelancer_Company_Name'],Company_Designation=self.validated_data['Company_Designation'],Company_Joining_date=self.validated_data['Company_Joining_date'],Company_Leaving_date=self.validated_data.get('Company_Leaving_date'),add_by=user) 
    
class FreelancerEmploymentUpdateSeralizer(serializers.ModelSerializer):
   
    class Meta:
        model = FreelancerEmployment
        fields = ['Freelancer_Company_Name','Company_Designation','Company_Joining_date','Company_Leaving_date'] 