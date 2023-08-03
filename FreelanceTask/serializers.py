from rest_framework import serializers
from . models import Project,Bid


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