from django.db import models
from account.models import Hirer,Freelancer
from django_fields import DefaultStaticImageField
from decimal import Decimal

# Create your models here.

class Project(models.Model):
    class Experience_level(models.TextChoices):
        Entry_Level = "Entry_Level", "entry_Level"
        Intermediate = "Intermediate", "intermediate"   
        Experienced = "Expert" , "expert"
    class Rate(models.TextChoices):
        Hourly = "Hourly", "hourly"
        Fixed = "Fixed", "fixed"
    title = models.CharField(max_length=200,default="")
    description = models.TextField(default="")
    deadline = models.DateField(blank=True,null=True)
    skills_required = models.CharField(max_length=200,default="")
    project_owner = models.ForeignKey(Hirer, on_delete=models.DO_NOTHING, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.TextField(default='')
    rate = models.CharField(max_length=15,choices=Rate.choices,default="")
    min_hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,null=True)
    max_hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,null=True)
    fixed_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    experience_level = models.CharField(max_length=50,choices=Experience_level.choices,default="")
    is_hired = models.BooleanField(default=False)

    class Meta:
        db_table="Project"
   

class Bid(models.Model):
    class Bid_Type(models.TextChoices):
        Hourly = "Hourly", "hourly"
        Fixed = "Fixed", "fixed"
    freelancer = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING,related_name='bid')
    project = models.ForeignKey(Project,on_delete=models.DO_NOTHING,related_name='bid')
    bid_amount = models.DecimalField(max_digits=10,decimal_places=2, blank=True, null=True)
    bid_type = models.CharField(choices=Bid_Type.choices,default="", max_length=15)
    description = models.TextField(default="")
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="Bid"


class Membership(models.Model):
    class membership_type(models.TextChoices):
        Freelancer = "Freelancer", "freelancer"
        Hirer = "Hirer", "hirer"
    name = models.CharField(max_length=255)
    features = models.CharField(default="",max_length=10000)
    price = models.DecimalField(max_digits=6, decimal_places=2,default="")
    duration = models.PositiveIntegerField(help_text='Duration in days',default="")
    membership_type = models.CharField(max_length=50,choices=membership_type.choices, default="")     

    class Meta:
        db_table="Membership"   


class Review(models.Model):
    RATING_CHOICES = [(Decimal(f"{i/2:.1f}"), Decimal(f"{i/2:.1f}")) for i in range(2, 11)]  

    review = models.TextField(default="")
    rating = models.DecimalField(max_digits=2, decimal_places=1, choices=RATING_CHOICES, default=Decimal("1.0"))
    created_by = models.ForeignKey(Hirer, on_delete=models.DO_NOTHING, related_name='reviews_created')
    created_for = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='reviews_received')
    created_at = models.DateTimeField(auto_now_add=True)
    projects = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='projects_completed')

    class Meta:
        db_table = "Review"




class FreelancerProject(models.Model):
    project_title = models.CharField(max_length=200,default="")
    project_description = models.TextField(default="")
    project_link=models.URLField(default="")
    images_logo=DefaultStaticImageField(upload_to="images_logo",default_image_path='images/blankpro.png',blank=True)
    project_pdf=models.FileField(upload_to='documents',default='doc/default.pdf',blank=True)
    skills_used = models.CharField(max_length=200,default="")
    design_by = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='selfprojects')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.TextField(default='')

    class Meta:
        db_table="FreelancerProject"


class SavedProject(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='saved_jobs')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='saved_projects')
    date_saved = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table="SavedProject"


class FreelancerEmployment(models.Model):
    
    Freelancer_Company_Name=models.CharField(max_length=50,default="")
    Company_Designation=models.CharField(max_length=100,default="")
    Company_Joining_date=models.DateField(blank=True,null=True)
    Company_Leaving_date=models.DateField(blank=True,null=True)
    add_by = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='employment')
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table="FreelancerEmployment"


class Subscription(models.Model):
    email = models.EmailField(unique=True, max_length=200)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="Subscription"

class UserContactUs(models.Model):
    Applicant_Email = models.EmailField(unique=True, max_length=200)
    Applicant_Name = models.CharField(max_length=25, default='')
    Applicant_Contact = models.CharField(max_length=10, default='')
    Message = models.TextField(default='') 

    class Meta:
        db_table="UserContactUs"


class ClientNotification(models.Model):
    hirer = models.ForeignKey(Hirer, on_delete=models.DO_NOTHING, related_name='hirer_notification')
    title = models.CharField(max_length=200)
    message = models.TextField(default='')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="ClientNotification"


class FreelancerNotification(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='freelancer_notification')
    title = models.CharField(max_length=200)
    message = models.TextField(default='')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="FreelancerNotification" 



class Hire(models.Model):
    class Hiring_Budget_Type(models.TextChoices):
        Hourly = "Hourly", "hourly"
        Fixed = "Fixed", "fixed"
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='hired_projects')
    hired_freelancer = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='hired_freelancers')
    freelancer_accepted = models.BooleanField(default=False)
    freelancer_rejected = models.BooleanField(default=False)
    project_title = models.CharField(max_length=255,default="")  
    hiring_budget = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True)  
    message = models.TextField(default="")  
    hiring_budget_type = models.CharField(choices=Hiring_Budget_Type.choices,default="", max_length=15)
    hired_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table="Hire" 
