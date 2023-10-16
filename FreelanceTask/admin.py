from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.



class ProjectsAdmin(UserAdmin):
    list_display = ('id','title','description','fixed_budget','deadline','skills_required','category','project_owner','rate','min_hourly_rate','max_hourly_rate','experience_level')
    list_filter = ('project_owner',)

    fieldsets = (
        (None, {'fields': ('title','category')}),
        ('Personal info', {'fields': ('description','fixed_budget','deadline','skills_required','rate','min_hourly_rate','max_hourly_rate','experience_level')}),
    )
    add_fieldsets = (
        (None, {'fields': ('title','category')}),
        ('Personal info', {'fields': ('description','fixed_budget','deadline','skills_required','rate','min_hourly_rate','max_hourly_rate','experience_level')}),
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


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('id','created_for','created_by','rating','review')
    list_filter = ('rating',)

    fieldsets = (
        (None, {'fields': ('created_for','rating')}),
        ('Personal info', {'fields': ('review','created_by')}),
    )
    add_fieldsets = (
        (None, {'fields': ('created_for','rating')}),
        ('Personal info', {'fields': ('review','created_by')}),
    )
    search_fields = ('rating',)
    ordering = ('id',)
    filter_horizontal = ()

    def has_add_permission(self, request):
        return False

admin.site.register(Review,ReviewsAdmin)