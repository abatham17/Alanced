from django.db import models
from account.models import Hirer,Freelancer
from django_fields import DefaultStaticImageField

# Create your models here.

class Project(models.Model):
    class Category(models.TextChoices):
         Web_development = "Web_development", "web_development"
         Mobile_development = "Mobile_development", "mobile_development"
         Web_designing = "Web_designing" , "web_designing"
         Software_development = "Software_development", "software_development"
         Ui_Ux_designing = "Ui_Ux_designing", "ui_ux_designing"
         Logo_Designing ="Logo_Designing", "logo_Designing"
         Graphics_designing ="Graphics_designing", "graphics_designing"
         Cloud_computing ="Cloud_computing", "cloud_computing"
         AI_ML ="AI_ML", "AI_ML"
         Data_Science ="Data_Science", "data_Science"
    title = models.CharField(max_length=200,default="")
    description = models.TextField(default="")
    budget = models.DecimalField(max_digits=10, decimal_places=2,default="")
    deadline = models.DateField(blank=True,null=True)
    skills_required = models.CharField(max_length=200,default="")
    project_owner = models.ForeignKey(Hirer, on_delete=models.DO_NOTHING, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(choices=Category.choices,default="",max_length=100)

    class Meta:
        db_table="Project"
   

class Bid(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING,related_name='bid')
    project = models.ForeignKey(Project,on_delete=models.DO_NOTHING,related_name='bid')
    bid_amount = models.DecimalField(max_digits=10,decimal_places=2)
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
    price = models.DecimalField(max_digits=10, decimal_places=2,default="")
    duration = models.PositiveIntegerField(help_text='Duration in days',default="")
    membership_type = models.CharField(choices=membership_type.choices, default="",max_length=100)     

    class Meta:
        db_table="Membership"   


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  

    review = models.TextField(default="")
    rating = models.IntegerField(choices=RATING_CHOICES,default="")
    created_by = models.ForeignKey(Hirer,on_delete=models.DO_NOTHING,related_name='reviews_created')
    created_for = models.ForeignKey(Freelancer,on_delete=models.DO_NOTHING,related_name='reviews_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="Review" 



class FreelancerProject(models.Model):
    class Category(models.TextChoices):
         Web_development = "Web_development", "web_development"
         Mobile_development = "Mobile_development", "mobile_development"
         Web_designing = "Web_designing" , "web_designing"
         Software_development = "Software_development", "software_development"
         Ui_Ux_designing = "Ui_Ux_designing", "ui_ux_designing"
         Logo_Designing ="Logo_Designing", "logo_Designing"
         Graphics_designing ="Graphics_designing", "graphics_designing"
         Cloud_computing ="Cloud_computing", "cloud_computing"
         AI_ML ="AI_ML", "AI_ML"
         Data_Science ="Data_Science", "data_Science"
    project_title = models.CharField(max_length=200,default="")
    project_description = models.TextField(default="")
    project_link=models.URLField(default="")
    images_logo=DefaultStaticImageField(upload_to="images_logo",default_image_path='images/blank.png',blank=True)
    project_pdf=models.FileField(upload_to='documents',default='images/default.pdf')
    skills_used = models.CharField(max_length=200,default="")
    design_by = models.ForeignKey(Freelancer, on_delete=models.DO_NOTHING, related_name='selfprojects')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(choices=Category.choices,default="",max_length=100)

    class Meta:
        db_table="FreelancerProject"