from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.



class ProjectsAdmin(UserAdmin):
    list_display = ('id','title','description','budget','deadline','skills_required','category','project_owner')
    list_filter = ('project_owner',)

    fieldsets = (
        (None, {'fields': ('title','category')}),
        ('Personal info', {'fields': ('description','budget','deadline','skills_required')}),
    )
    add_fieldsets = (
        (None, {'fields': ('title','category')}),
        ('Personal info', {'fields': ('description','budget','deadline','skills_required')}),
    )
    # readonly_fields=('last_login',)
    search_fields = ('category',)
    ordering = ('id',)
    filter_horizontal = ()

    def has_add_permission(self, request):
        return False

admin.site.register(Project,ProjectsAdmin)


class MembershipsAdmin(admin.ModelAdmin):
    list_display = ('id','name','features','price','duration','membership_type')
    list_filter = ('name',)

    fieldsets = (
        (None, {'fields': ('name','duration')}),
        ('Personal info', {'fields': ('features','price','membership_type')}),
    )
    add_fieldsets = (
        (None, {'fields': ('name','duration')}),
        ('Personal info', {'fields': ('features','price','membership_type')}),
    )
    # readonly_fields=('last_login',)
    search_fields = ('name',)
    ordering = ('id',)
    filter_horizontal = ()

admin.site.register(Membership,MembershipsAdmin)