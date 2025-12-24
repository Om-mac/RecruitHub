from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
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
    
    def get_queryset(self, request):
        """Exclude HR accounts from UserProfile list (show only student profiles)"""
        qs = super().get_queryset(request)
        # Filter out users who have HR profiles
        hr_user_ids = HRProfile.objects.values_list('user_id', flat=True)
        return qs.exclude(user_id__in=hr_user_ids)
    
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
            # Delete the user first, which will cascade delete the profile
            user.delete()
        else:
            super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Delete users when deleting multiple profiles at once"""
        for obj in queryset:
            if obj.user:
                obj.user.delete()
            else:
                obj.delete()
    
    def permanently_delete_user(self, request, queryset):
        """Custom action to permanently delete selected users and all related data"""
        deleted_count = 0
        for profile in queryset:
            if profile.user:
                username = profile.user.username
                profile.user.delete()
                deleted_count += 1
        self.message_user(request, f"✓ Successfully deleted {deleted_count} user(s) and all related data from database")
    permanently_delete_user.short_description = "🗑️ Permanently delete selected users from database"
    
    def create_50_fake_users(self, request, queryset):
        """Create 10 test users (22IF001-22IF010) with complete profiles"""
        try:
            from faker import Faker
            import random
            from django.db import transaction
            
            fake = Faker()
            branches = ['CSE', 'ECE', 'Mechanical', 'Civil', 'EEE', 'IT', 'Production']
            years = ['1', '2', '3', '4']
            genders = ['M', 'F', 'O']
            skills_list = [
                'Python, Java, JavaScript', 'Python, Django, React',
                'Java, Spring Boot, MySQL', 'JavaScript, Node.js, MongoDB',
                'C++, Data Structures, Algorithms', 'Python, Machine Learning, TensorFlow',
                'Full Stack: React, Django, PostgreSQL', 'Backend: Node.js, Express, PostgreSQL',
                'Mobile: Flutter, Kotlin', 'Web: HTML, CSS, JavaScript, Bootstrap',
            ]
            
            created_count = 0
            skipped_count = 0
            User = get_user_model()
            
            # Pre-check existing users
            existing_usernames = set(User.objects.filter(
                username__startswith='22IF'
            ).values_list('username', flat=True))
            
            with transaction.atomic():
                # Create all users in one transaction
                for i in range(1, 11):  # Create 10 users instead of 50
                    username = f'22IF{i:03d}'
                    if username in existing_usernames:
                        skipped_count += 1
                        continue
                    
                    password = f'{username}{username}'
                    email = f'{username}@college.edu'
                    
                    user = User.objects.create_user(
                        username=username, email=email, password=password,
                        first_name=fake.first_name(), last_name=fake.last_name(),
                    )
                    created_count += 1
                
                # Now create profiles for all users
                UserProfile = get_user_model().profile.field.related_model
                profiles = []
                for i in range(1, 11):  # Create 10 users instead of 50
                    username = f'22IF{i:03d}'
                    if username in existing_usernames:
                        continue
                    
                    user = User.objects.get(username=username)
                    profile = user.profile
                    profile.middle_name = fake.first_name()
                    profile.phone = fake.phone_number()[:15]
                    profile.date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=25)
                    profile.gender = random.choice(genders)
                    profile.address = fake.address()
                    profile.city = fake.city()
                    profile.state = fake.state()
                    profile.pincode = fake.postcode()[:10]
                    profile.college_name = 'XYZ College of Engineering'
                    profile.branch = random.choice(branches)
                    profile.degree = 'B.Tech'
                    profile.specialization = profile.branch
                    profile.cgpa = round(random.uniform(6.5, 9.2), 2)
                    profile.year_of_study = random.choice(years)
                    profile.admission_year = random.randint(2020, 2023)
                    profile.backlogs = random.randint(0, 3)
                    profile.current_backlogs = random.randint(0, 2)
                    profile.skills = random.choice(skills_list)
                    profile.github_username = fake.user_name()
                    profile.linkedin_username = fake.user_name()
                    profile.hackerrank_username = fake.user_name()
                    profile.experience = f'{random.randint(0, 3)} years'
                    profile.bio = fake.text(max_nb_chars=200)
                    profile.save()
            
            msg = f'✅ Created {created_count} test users (22IF001-22IF010)'
            if skipped_count > 0:
                msg += f' | {skipped_count} already existed'
            self.message_user(request, msg)
            
        except ImportError:
            self.message_user(request, '❌ Faker library not installed', level='ERROR')
        except Exception as e:
            self.message_user(request, f'❌ Error: {str(e)}', level='ERROR')
    
    create_50_fake_users.short_description = "⚡ Create 10 Test Users (22IF001-22IF010)"
    
    actions = ['delete_selected', 'permanently_delete_user', 'create_50_fake_users']
    
    def college_badge(self, obj):
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
    list_display = ['user_badge', 'company_badge', 'designation', 'department', 'approval_status_badge', 'approval_requested_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'company_name']
    list_filter = ['is_approved', 'department', 'approval_requested_at', 'created_at']
    readonly_fields = ('user', 'created_at', 'approval_requested_at', 'approved_at', 'approval_token', 'approval_status_info')
    
    fieldsets = (
        ('User Info', {'fields': ('user', 'created_at')}),
        ('Company Info', {'fields': ('company_name', 'designation', 'department')}),
        ('Approval Status', {
            'fields': ('is_approved', 'approval_status_info', 'approval_requested_at', 'approved_by', 'approved_at', 'approval_token', 'rejection_reason'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Ensure HR account is properly configured as staff and not a student"""
        if not change:  # Only on creation
            # Make HR user a staff member
            obj.user.is_staff = True
            obj.user.save()
        super().save_model(request, obj, form, change)
    
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
    
    def approval_status_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="background: #f39c12; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">⏳ Pending</span>'
            )
    approval_status_badge.short_description = 'Status'
    
    def approval_status_info(self, obj):
        if obj.is_approved:
            return format_html(
                '<p style="color: #27ae60; font-weight: bold;">✓ Account Approved</p>' +
                f'<p>Approved by: {obj.approved_by.username if obj.approved_by else "System"}</p>' +
                f'<p>Approved at: {obj.approved_at.strftime("%Y-%m-%d %H:%M:%S") if obj.approved_at else "N/A"}</p>'
            )
        else:
            return format_html(
                '<p style="color: #e74c3c; font-weight: bold;">⏳ Account Pending Approval</p>' +
                f'<p>Requested at: {obj.approval_requested_at.strftime("%Y-%m-%d %H:%M:%S") if obj.approval_requested_at else "N/A"}</p>' +
                '<p><a class="button" href="/admin/approve-hr/' + (obj.approval_token or '') + '/" style="background: #27ae60; color: white; padding: 8px 12px; border-radius: 4px; text-decoration: none; display: inline-block; margin-right: 10px;">✓ Approve</a>' +
                '<a class="button" href="/admin/reject-hr/' + (obj.approval_token or '') + '/" style="background: #e74c3c; color: white; padding: 8px 12px; border-radius: 4px; text-decoration: none; display: inline-block;">✗ Reject</a></p>'
            )
    approval_status_info.short_description = 'Approval Information'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and show pending approvals first"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'approved_by').order_by('is_approved', '-approval_requested_at')

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
    readonly_fields = ('user', 'created_at')
    
    fieldsets = (
        ('Note Info', {'fields': ('user', 'title', 'created_at')}),
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


# Register User model - ONLY shows student accounts (not HR staff)
@admin.register(User, site=custom_admin)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username_display', 'first_name', 'last_name', 'email', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['is_active', 'date_joined']
    readonly_fields = ('username', 'is_staff', 'is_superuser')
    
    def get_queryset(self, request):
        """Only show student accounts (exclude all staff/superuser accounts)"""
        qs = super().get_queryset(request)
        # Exclude all staff and superuser accounts (HR and admin users)
        return qs.filter(is_staff=False, is_superuser=False).select_related('profile')
    
    def username_display(self, obj):
        return format_html(
            '<span style="background: #667eea; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">🎓 {}</span>',
            obj.username
        )
    username_display.short_description = 'Username'
    
    def has_delete_permission(self, request, obj=None):
        """Allow superuser to delete users"""
        return request.user.is_superuser
