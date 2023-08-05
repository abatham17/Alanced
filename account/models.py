from django.db import models
from django.contrib.auth.models import( BaseUserManager, AbstractBaseUser)
from django.core.validators import MaxValueValidator
from django_fields import DefaultStaticImageField

# Create your models here.

class UserAccountManager(BaseUserManager):
	def create_user(self , email , password = None):
		if not email or len(email) <= 0 :
			raise ValueError("Email field is required !")
		if not password :
			raise ValueError("Password is must !")
		
		user = self.model(
			email = self.normalize_email(email) ,
		)
		user.set_password(password)
		user.save(using = self._db)
		return user
	
	def create_superuser(self , email , password):
		user = self.create_user(
			email = self.normalize_email(email) ,
			password = password
		)
		user.is_admin = True
		user.is_superuser = True
		user.save(using = self._db)
		return user
	
class UserAccount(AbstractBaseUser):
    class Types(models.TextChoices):
        OWNER = "OWNER" , "owner"
        HIRER = "HIRER" , "hirer"
                
        
        FREELANCER="FREELANCER","freelancer"
    class gender(models.TextChoices):
        Male = "Male", "male"
        Female = "Female", "female"
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
    date_of_creation = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    images_logo=DefaultStaticImageField(upload_to="images_logo",default_image_path='images/blank.png',blank=True)
    type = models.CharField(max_length = 20 , choices = Types.choices ,
                            default = Types.OWNER)
    email = models.EmailField(max_length = 200 , unique = True)
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)
    is_hirer = models.BooleanField(default = False)
    is_superuser = models.BooleanField(default = False)
    Company_Name=models.CharField(max_length=50,default="")
    is_freelancer = models.BooleanField(default = False)   
    is_owner = models.BooleanField(default = False)
    first_Name=models.CharField(max_length=25,default='')
    last_Name=models.CharField(max_length=25,default='')
    experience=models.PositiveIntegerField(validators=[MaxValueValidator(99)],default=0)
    qualification=models.TextField(default='')
    contact=models.CharField(max_length=10)
    about=models.TextField(default="")
    Company_Establish=models.DateField(blank=True,null=True)
    skills=models.TextField(default="")
    social_media=models.URLField(default="")
    Block=models.BooleanField(default=False)
    map=models.URLField(default="")
    Address=models.TextField(default="")
    DOB=models.DateField(blank=True,null=True)
    category = models.CharField(choices=Category.choices,default="",max_length=100)
    gender=models.CharField(max_length=8,choices=gender.choices,default=gender.Male)
    
    USERNAME_FIELD = "email"
    
    # defining the manager for the UserAccount model
    objects = UserAccountManager()
    
    def __str__(self):
        return str(self.email)
    
    def has_perm(self , perm, obj = None):
        return self.is_admin
    
    def has_module_perms(self , app_label):
        return True
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
        
    def save(self , *args , **kwargs):
        if not self.type or self.type == None :
            self.type = UserAccount.Types.OWNER
        return super().save(*args , **kwargs)




class OwnerManager(models.Manager):
    def create_user(self , email , password = None):
        if not email or len(email) <= 0 : 
            raise  ValueError("Email field is required !")
        if not password :
            raise ValueError("Password is must !")
        email  = email.lower()
        user = self.model(
            email = email
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
      
    def get_queryset(self , *args,  **kwargs):
        queryset = super().get_queryset(*args , **kwargs)
        queryset = queryset.filter(type = UserAccount.Types.OWNER)
        return queryset    



class Owner(UserAccount):
    class Meta : 
        proxy = True
    objects = OwnerManager()
      
    def save(self , *args , **kwargs):
        self.type = UserAccount.Types.OWNER
        self.is_owner = True
        return super().save(*args , **kwargs)
    
    def __str__(self):
        return str(self.Company_Name)
      
class HirerManager(models.Manager):
    def create_user(self , email , password = None):
        if not email or len(email) <= 0 : 
            raise  ValueError("Email field is required !")
        if not password :
            raise ValueError("Password is must !")
        email = email.lower()
        user = self.model(
            email = email
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
        
    def get_queryset(self , *args , **kwargs):
        queryset = super().get_queryset(*args , **kwargs)
        queryset = queryset.filter(type = UserAccount.Types.HIRER)
        return queryset
      
class Hirer(UserAccount):
    class Meta :
        proxy = True
    objects = HirerManager()
      
    def save(self  , *args , **kwargs):
        self.type = UserAccount.Types.HIRER
        self.is_hirer = True
        return super().save(*args , **kwargs)
    
    def __str__(self):
        return str(self.id)
    

class FreelancerManager(models.Manager):
    def create_user(self , email , password = None):
        if not email or len(email) <= 0 : 
            raise  ValueError("Email field is required !")
        if not password :
            raise ValueError("Password is must !")
        email  = email.lower()
        user = self.model(
            email = email
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
      
    def get_queryset(self , *args,  **kwargs):
        queryset = super().get_queryset(*args , **kwargs)
        queryset = queryset.filter(type = UserAccount.Types.FREELANCER)
        return queryset    



class Freelancer(UserAccount):
    class Meta : 
        proxy = True
    objects = FreelancerManager()
      
    def save(self , *args , **kwargs):
        self.type = UserAccount.Types.FREELANCER
        self.is_freelancer = True
        return super().save(*args , **kwargs)
    
    def __str__(self):
        return str(self.first_Name)

