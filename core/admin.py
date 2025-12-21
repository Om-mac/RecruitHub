from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, Document, Note, HRProfile, EmailOTP

# Custom Admin Site with Enhanced Styling
class CustomAdminSite(admin.AdminSite):
    site_header = "🎓 RecruitHub Admin Dashboard"
    site_title = "RecruitHub Admin"
    index_title = "Welcome to RecruitHub Administration"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['site_name'] = 'RecruitHub'
        return super().index(request, extra_context)

# Create custom admin site instance
custom_admin = CustomAdminSite(name='recruitHub_admin')

@admin.register(UserProfile, site=custom_admin)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_badge', 'college_badge', 'branch', 'degree', 'year_display', 'cgpa_badge', 'github_username', 'delete_user_link']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'college_name', 'branch', 'phone', 'specialization', 'github_username', 'linkedin_username']
    list_filter = ['branch', 'degree', 'gender', 'year_of_study', 'admission_year', 'cgpa', 'date_of_birth']
    readonly_fields = ('user', 'created_at')
    actions = ['delete_selected']
    
    fieldsets = (
        ('User Info', {'fields': ('user', 'created_at')}),
        ('Personal Details', {'fields': ('middle_name', 'date_of_birth', 'gender', 'phone', 'address', 'city', 'state', 'pincode', 'profile_photo')}),
        ('Education', {'fields': ('college_name', 'branch', 'degree', 'specialization', 'cgpa', 'year_of_study', 'admission_year', 'backlogs', 'current_backlogs')}),
        ('Certifications', {'fields': ('certifications_links',)}),
        ('Online Profiles', {'fields': ('github_username', 'linkedin_username', 'hackerrank_username', 'other_platforms')}),
        ('Professional', {'fields': ('experience', 'resume', 'skills', 'bio')}),
    )
    
    def user_badge(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;"><span style="background: #667eea; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">👤 {}</span></div>',
            obj.user.username
        )
    user_badge.short_description = 'User'
    
    def delete_user_link(self, obj):
        """Show a delete button to remove both user and profile"""
        from django.urls import reverse
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html(
            '<a class="button" style="background: #e74c3c; color: white; padding: 8px 12px; border-radius: 4px; text-decoration: none;" href="{}?next={}">🗑️ Delete User</a>',
            url,
            reverse('admin:core_userprofile_changelist')
        )
    delete_user_link.short_description = 'Action'
    
    def has_delete_permission(self, request, obj=None):
        """Allow superuser to delete profiles"""
        return request.user.is_superuser
    
    def delete_model(self, request, obj):
        """Delete the associated User when UserProfile is deleted"""
        if obj.user:
            user = obj.user
            super().delete_model(request, obj)
            user.delete()
        else:
            super().delete_model(request, obj)
        return format_html(
            '<span style="background: #764ba2; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px;">🏫 {}</span>',
            obj.college_name if obj.college_name else 'N/A'
        )
    college_badge.short_description = 'College'
    
    def year_display(self, obj):
        year_colors = {
            '1st Year': '#FF6B6B',
            '2nd Year': '#4ECDC4',
            '3rd Year': '#45B7D1',
            '4th Year': '#96CEB4',
        }
        color = year_colors.get(obj.get_year_of_study_display(), '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">{}</span>',
            color,
            obj.get_year_of_study_display()
        )
    year_display.short_description = 'Year'
    
    def cgpa_badge(self, obj):
        if not obj.cgpa:
            return '-'
        cgpa = float(obj.cgpa)
        if cgpa >= 3.5:
            color = '#2ecc71'
        elif cgpa >= 3.0:
            color = '#3498db'
        elif cgpa >= 2.5:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">⭐ {}</span>',
            color,
            obj.cgpa
        )
    cgpa_badge.short_description = 'CGPA'

@admin.register(HRProfile, site=custom_admin)
class HRProfileAdmin(admin.ModelAdmin):
    list_display = ['user_badge', 'company_badge', 'designation', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'company_name']
    list_filter = ['department', 'created_at']
    readonly_fields = ('user', 'created_at')
    
    fieldsets = (
        ('User Info', {'fields': ('user', 'created_at')}),
        ('Company Info', {'fields': ('company_name', 'designation', 'department')}),
    )
    
    def user_badge(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">👤 {}</span>',
            obj.user.username
        )
    user_badge.short_description = 'User'
    
    def company_badge(self, obj):
        return format_html(
            '<span style="background: #764ba2; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px;">🏢 {}</span>',
            obj.company_name if obj.company_name else 'N/A'
        )
    company_badge.short_description = 'Company'

@admin.register(Document, site=custom_admin)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title_display', 'user_badge', 'file_type_badge', 'uploaded_at', 'file_size_display']
    search_fields = ['title', 'user__username']
    list_filter = ['uploaded_at']
    readonly_fields = ('user', 'uploaded_at', 'file_preview')
    
    fieldsets = (
        ('Document Info', {'fields': ('user', 'title', 'uploaded_at')}),
        ('File Details', {'fields': ('file', 'file_preview')}),
    )
    
    def title_display(self, obj):
        return format_html(
            '<strong>📄 {}</strong>',
            obj.title[:40] if obj.title else '(Untitled)'
        )
    title_display.short_description = 'Document'
    
    def user_badge(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 4px 8px; border-radius: 15px; font-size: 11px;">{}</span>',
            obj.user.username
        )
    user_badge.short_description = 'User'
    
    def file_type_badge(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].upper()
            color = '#3498db'
            return format_html(
                '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 15px; font-size: 11px; font-weight: bold;">.{}</span>',
                color,
                ext
            )
        return '-'
    file_type_badge.short_description = 'Type'
    
    def file_size_display(self, obj):
        if obj.file:
            size = obj.file.size / 1024
            if size > 1024:
                size_str = f"{size/1024:.2f} MB"
            else:
                size_str = f"{size:.2f} KB"
            return format_html(
                '<span style="color: #555; font-weight: 500;">📊 {}</span>',
                size_str
            )
        return "-"
    file_size_display.short_description = 'Size'
    
    def file_preview(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="padding: 8px 16px; background: #667eea; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;">📥 Download</a>',
                obj.file.url
            )
        return "-"
    file_preview.short_description = 'Download'

@admin.register(Note, site=custom_admin)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title_display', 'user_badge', 'word_count_badge', 'created_at']
    search_fields = ['title', 'user__username']
    list_filter = ['created_at']
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Note Info', {'fields': ('user', 'title', 'created_at', 'updated_at')}),
        ('Content', {'fields': ('content',)}),
    )
    
    def title_display(self, obj):
        return format_html(
            '<strong>📝 {}</strong>',
            obj.title[:40] if obj.title else '(Untitled)'
        )
    title_display.short_description = 'Note'
    
    def user_badge(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 4px 8px; border-radius: 15px; font-size: 11px;">{}</span>',
            obj.user.username
        )
    user_badge.short_description = 'User'
    
    def word_count_badge(self, obj):
        count = len(obj.content.split()) if obj.content else 0
        return format_html(
            '<span style="background: #2ecc71; color: white; padding: 4px 8px; border-radius: 15px; font-size: 11px; font-weight: bold;">✍️ {} words</span>',
            count
        )
    word_count_badge.short_description = 'Words'

@admin.register(EmailOTP, site=custom_admin)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email_display', 'otp_display', 'created_at', 'validity_badge']
    search_fields = ['email']
    list_filter = ['created_at']
    readonly_fields = ('email', 'otp', 'created_at')
    
    fieldsets = (
        ('OTP Info', {'fields': ('email', 'otp', 'created_at')}),
    )
    
    def email_display(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 6px 12px; border-radius: 20px;">📧 {}</span>',
            obj.email
        )
    email_display.short_description = 'Email'
    
    def otp_display(self, obj):
        return format_html(
            '<span style="background: #f39c12; color: white; padding: 6px 12px; border-radius: 5px; font-family: monospace; font-weight: bold; font-size: 14px;">🔐 {}</span>',
            obj.otp
        )
    otp_display.short_description = 'OTP'
    
    def validity_badge(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        is_valid = timezone.now() - obj.created_at < timedelta(minutes=10)
        if is_valid:
            return format_html(
                '<span style="background: #2ecc71; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">✓ Valid</span>'
            )
        else:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">✗ Expired</span>'
            )
    validity_badge.short_description = 'Status'


# Register User model with custom delete functionality
@admin.register(User, site=custom_admin)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    
    def has_delete_permission(self, request, obj=None):
        """Allow superuser to delete users"""
        return request.user.is_superuser
