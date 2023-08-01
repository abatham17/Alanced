from rest_framework import serializers
from . models import Project,Membership,Review
from account.models import Freelancer


class AddProjectSerializer(serializers.ModelSerializer):
    skills_required=serializers.ListField(child=serializers.CharField())
    category = serializers.ChoiceField(choices=["Web_development","Mobile_development","Web_designing","Software_development","Ui_Ux_designing","Logo_Designing","Graphics_designing","Cloud_computing","AI_ML","Data_Science"])
    class Meta:
        model=Project
        fields=['title','description','budget','deadline','skills_required','category']

    def validate(self, attrs):
        user=self.context.get('user')
        if user.Block==True:
            raise serializers.ValidationError("Your Profile is Blocked")
        elif user.is_hirer!=True:
            raise serializers.ValidationError("You're not a Hirer Profile") 
        return attrs    
    
    def create(self, validated_data):
        user=self.context.get('user')
        return Project.objects.create(title=self.validated_data['title'],description=self.validated_data['description'],budget=self.validated_data['budget'],deadline=self.validated_data['deadline'],skills_required=self.validated_data['skills_required'],category=self.validated_data['category'],project_owner=user)
    

class ViewAllProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','title','description','budget','deadline','skills_required','category','project_owner_id']


class ProjectUpdateSeralizer(serializers.ModelSerializer):
    skills_required=serializers.ListField(child=serializers.CharField())
    class Meta:
        model = Project
        fields = ['title','description','budget','deadline','skills_required','category']


class ViewAllMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['name','features','price','duration','membership_type']


class AddReviewSeralizer(serializers.ModelSerializer):
    # rating = serializers.IntegerField(choices=RATING_CHOICES,default="")
    class Meta:
        model = Review
        fields = ['rating','review']    


    def create(self, validated_data):
        user=self.context.get('user')
        free_id=self.context.get('free_id')
        freelancer_id=Freelancer.objects.get(id=free_id)
        return Review.objects.create(rating=self.validated_data['rating'],review=self.validated_data['review'],created_by=user,created_for=freelancer_id)         

  