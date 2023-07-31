from django.db import models
from account.models import Hirer,Freelancer

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
    category = models.CharField(choices=Category.choices,default="")

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