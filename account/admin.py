from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
# admin.site.register(UserAccount)

class OwnerAdmin(UserAdmin):
    list_display = ('email','is_owner','Company_Name','first_Name','last_Name','contact','gender','DOB','Address')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('email', 'password','last_login')}),
        ('Personal info', {'fields': ('is_owner','Company_Name','first_Name','last_Name','contact','images_logo','gender','DOB','Address')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Personal info', {'fields': ('is_owner','Company_Name','first_Name','last_Name','contact','images_logo','gender','DOB','Address')}),
    )
    readonly_fields=('last_login',)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_add_permission(self, request):
        return False

admin.site.register(Owner,OwnerAdmin)


class HirerAdmin(UserAdmin):
    list_display = ('email','is_hirer','first_Name','last_Name','contact','Block','about','Company_Establish','social_media','map','Address','DOB','gender','Company_Name','images_logo','is_verified')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('email', 'password','last_login')}),
        ('Personal info', {'fields': ('Block','is_verified')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Personal info', {'fields': ('is_hirer','first_Name','last_Name','images_logo','contact','Block','is_verified','about','Company_Establish','social_media','map','Address','DOB','gender','Company_Name','images_logo','is_verified')}),
    )
    readonly_fields=('last_login',)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_add_permission(self, request):
        return False

admin.site.register(Hirer,HirerAdmin)

class FreelancerAdmin(UserAdmin):
    list_display = ('email','is_freelancer','first_Name','last_Name','Block','images_logo','about','social_media','map','Address','DOB','gender','experience','qualification','skills','category','is_verified')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('email', 'password','last_login')}),
        ('Personal info', {'fields': ('Block','is_verified')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Personal info', {'fields': ('is_freelancer','first_Name','last_Name','contact','images_logo','Block','about','social_media','map','Address','DOB','gender','experience','qualification','skills','category','is_verified')}),
    )
    
    readonly_fields=('last_login',)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_add_permission(self, request):
        return False

admin.site.register(Freelancer,FreelancerAdmin)