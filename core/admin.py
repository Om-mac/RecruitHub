from django.contrib import admin
from .models import UserProfile, Document, Note, HRProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'college_name', 'branch', 'degree', 'year_of_study', 'cgpa', 'current_backlogs', 'github_username']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'college_name', 'branch', 'phone', 'specialization', 'github_username', 'linkedin_username']
    list_filter = ['branch', 'degree', 'gender', 'year_of_study', 'admission_year', 'cgpa', 'date_of_birth']
    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Personal Details', {'fields': ('middle_name', 'date_of_birth', 'gender', 'phone', 'address', 'city', 'state', 'pincode', 'profile_photo')}),
        ('Education', {'fields': ('college_name', 'branch', 'degree', 'specialization', 'cgpa', 'year_of_study', 'admission_year', 'backlogs', 'current_backlogs')}),
        ('Certifications', {'fields': ('certifications_links',)}),
        ('Online Profiles', {'fields': ('github_username', 'linkedin_username', 'hackerrank_username', 'other_platforms')}),
        ('Professional', {'fields': ('experience', 'resume', 'skills', 'bio')}),
    )

@admin.register(HRProfile)
class HRProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'designation', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'company_name']
    list_filter = ['department', 'created_at']
    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Company Info', {'fields': ('company_name', 'designation', 'department')}),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'uploaded_at']
    search_fields = ['title', 'user__username']
    list_filter = ['uploaded_at']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at']
    search_fields = ['title', 'user__username']
    list_filter = ['created_at']
