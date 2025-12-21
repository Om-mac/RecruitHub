from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string
import threading
import logging
from .models import Document, Note, UserProfile, HRProfile, EmailOTP
from .forms import DocumentForm, NoteForm, UserRegistrationForm, UserProfileForm, HRLoginForm, HRRegistrationForm, HRProfileForm, PasswordResetForm, SetPasswordForm, ChangePasswordForm, OTPForm, EmailOTPForm

User = get_user_model()
logger = logging.getLogger('core')

def home(request):
    """Home page - redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Profile is auto-created via signal
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'core/profile.html', {'form': form, 'profile': profile})

@login_required(login_url='login')
def dashboard(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Process skills - split by comma
    if profile.skills:
        profile.skills_list = [skill.strip() for skill in profile.skills.split(',')]
    else:
        profile.skills_list = []
    
    documents = Document.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)
    return render(request, 'core/dashboard.html', {
        'documents': documents,
        'notes': notes,
        'profile': profile
    })

@login_required(login_url='login')
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error uploading document.')
    else:
        form = DocumentForm()
    return render(request, 'core/upload_document.html', {'form': form})

@login_required(login_url='login')
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Note added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error adding note.')
    else:
        form = NoteForm()
    return render(request, 'core/add_note.html', {'form': form})


@login_required(login_url='login')
def view_note(request, note_id):
    """View individual note"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    return render(request, 'core/view_note.html', {'note': note})


@login_required(login_url='login')
def edit_note(request, note_id):
    """Edit individual note"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('view_note', note_id=note.id)
        else:
            messages.error(request, 'Error updating note.')
    else:
        form = NoteForm(instance=note)
    return render(request, 'core/edit_note.html', {'form': form, 'note': note})


@login_required(login_url='login')
def delete_note(request, note_id):
    """Delete individual note"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'core/delete_note.html', {'note': note})


# HR Views
def hr_login(request):
    """HR Login Page"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'hr_profile'):
            return redirect('hr_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = HRLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if user has HR profile
                if hasattr(user, 'hr_profile'):
                    login(request, user)
                    messages.success(request, f'Welcome HR {user.first_name}!')
                    return redirect('hr_dashboard')
                else:
                    messages.error(request, 'You do not have HR access. Please contact administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = HRLoginForm()
    
    return render(request, 'core/hr_login.html', {'form': form})


def hr_register(request):
    """HR Registration Page - Note: Admin approval might be needed"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'hr_profile'):
            return redirect('hr_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = HRRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # Create HR Profile
            hr_profile = HRProfile.objects.create(
                user=user,
                company_name=request.POST.get('company_name', ''),
                designation=request.POST.get('designation', ''),
                department=request.POST.get('department', '')
            )
            
            messages.success(request, 'HR Registration successful! Please log in.')
            return redirect('hr_login')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = HRRegistrationForm()
    
    return render(request, 'core/hr_register.html', {'form': user_form})


@login_required(login_url='hr_login')
def hr_dashboard(request):
    """HR Dashboard - View and filter students"""
    # Check if user has HR profile
    if not hasattr(request.user, 'hr_profile'):
        messages.error(request, 'You do not have access to HR dashboard.')
        return redirect('dashboard')
    
    # Get all user profiles (students) - EXCLUDE HR USERS
    # Filter out users who have HR profiles
    hr_user_ids = HRProfile.objects.values_list('user_id', flat=True)
    students = UserProfile.objects.select_related('user').exclude(user_id__in=hr_user_ids)
    
    # Filtering
    branch_filter = request.GET.get('branch', '')
    cgpa_min = request.GET.get('cgpa_min', '')
    cgpa_max = request.GET.get('cgpa_max', '')
    backlogs_filter = request.GET.get('backlogs', '')
    
    filters = Q()
    
    if branch_filter:
        filters &= Q(branch__icontains=branch_filter)
    
    if cgpa_min:
        try:
            filters &= Q(cgpa__gte=float(cgpa_min))
        except (ValueError, TypeError):
            pass
    
    if cgpa_max:
        try:
            filters &= Q(cgpa__lte=float(cgpa_max))
        except (ValueError, TypeError):
            pass
    
    if backlogs_filter:
        try:
            backlogs_filter = int(backlogs_filter)
            filters &= Q(current_backlogs__lte=backlogs_filter)
        except (ValueError, TypeError):
            pass
    
    students = students.filter(filters)
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-cgpa')
    if sort_by in ['-cgpa', 'cgpa', '-current_backlogs', 'current_backlogs', 'user__first_name', '-user__first_name', 'branch']:
        students = students.order_by(sort_by)
    
    # Get unique branches for filter dropdown
    branches = UserProfile.objects.values_list('branch', flat=True).distinct().exclude(branch='')
    
    context = {
        'students': students,
        'branches': branches,
        'current_branch': branch_filter,
        'current_cgpa_min': cgpa_min,
        'current_cgpa_max': cgpa_max,
        'current_backlogs': backlogs_filter,
        'current_sort': sort_by,
    }
    
    return render(request, 'core/hr_dashboard.html', context)


@login_required(login_url='hr_login')
def student_detail(request, user_id):
    """View detailed profile of a student"""
    # Check if user has HR profile
    if not hasattr(request.user, 'hr_profile'):
        messages.error(request, 'You do not have access to student details.')
        return redirect('dashboard')
    
    student = get_object_or_404(UserProfile, user_id=user_id)
    
    # Process skills - split by comma
    if student.skills:
        student.skills_list = [skill.strip() for skill in student.skills.split(',')]
    else:
        student.skills_list = []
    
    return render(request, 'core/student_detail.html', {'student': student})


def hr_logout(request):
    """HR Logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('hr_login')

def password_reset_request(request):
    """Handle password reset request"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                # Create reset link
                reset_link = request.build_absolute_uri(f'/password_reset_confirm/{uid}/{token}/')
                
                # Send email in background thread
                def _send_reset_email():
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                
                thread = threading.Thread(target=_send_reset_email, daemon=True)
                thread.start()
                
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('password_reset_done')
            except User.DoesNotExist:
                # For security, show same message even if user doesn't exist
                messages.success(request, 'If an account with this email exists, you will receive a password reset link.')
                return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'core/password_reset.html', {'form': form})


def password_reset_done(request):
    """Show confirmation message after reset request"""
    return render(request, 'core/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    """Confirm password reset token and allow user to set new password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
                return redirect('login')
        else:
            form = SetPasswordForm()
        return render(request, 'core/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('password_reset_request')


@login_required(login_url='login')
def change_password(request):
    """Allow logged-in users to change their password"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            # Verify old password
            if user.check_password(form.cleaned_data['old_password']):
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'Your password has been changed successfully.')
                return redirect('password_change_done')
            else:
                form.add_error('old_password', 'Current password is incorrect.')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'core/change_password.html', {'form': form})


@login_required(login_url='login')
def password_change_done(request):
    """Show confirmation message after password change"""
    return render(request, 'core/password_change_done.html')


def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp):
    """Send OTP via email in background thread"""
    def _send_email():
        try:
            subject = 'Email Verification OTP - RecruitHub'
            message = f'''
Hello,

Your email verification OTP is: {otp}

This OTP is valid for 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
RecruitHub Team
        '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
    
    # Send email in background thread so request doesn't wait
    thread = threading.Thread(target=_send_email, daemon=True)
    thread.start()


def register_step1_email(request):
    """Step 1: Enter email and send OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if email already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return redirect('register_step1_email')
            
            # Generate and save OTP
            try:
                otp_obj = EmailOTP.objects.filter(email=email).first()
                if otp_obj:
                    # Delete old OTP record
                    otp_obj.delete()
                
                otp = generate_otp()
                EmailOTP.objects.create(email=email, otp=otp)
                
                # Send OTP via email
                send_otp_email(email, otp)
                
                # Store email in session for next step
                request.session['registration_email'] = email
                
                messages.success(request, f'OTP sent to {email}. Please check your inbox.')
                return redirect('register_step2_verify_otp')
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
                return redirect('register_step1_email')
    else:
        form = EmailOTPForm()
    
    return render(request, 'core/register_step1_email.html', {'form': form})


def register_step2_verify_otp(request):
    """Step 2: Verify OTP"""
    email = request.session.get('registration_email')
    
    if not email:
        messages.error(request, 'Please start registration process again.')
        return redirect('register_step1_email')
    
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            try:
                otp_obj = EmailOTP.objects.get(email=email)
                
                # Check if OTP is expired
                if otp_obj.is_expired():
                    otp_obj.delete()
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('register_step1_email')
                
                # Check if too many failed attempts
                if not otp_obj.is_valid_attempt():
                    otp_obj.delete()
                    messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                    return redirect('register_step1_email')
                
                # Check if OTP matches
                if otp_obj.otp == otp:
                    # Mark as verified and proceed to registration
                    otp_obj.is_verified = True
                    otp_obj.save()
                    request.session['otp_verified'] = True
                    return redirect('register_step3_create_account')
                else:
                    # Increment failed attempts
                    otp_obj.attempts += 1
                    otp_obj.save()
                    remaining = 5 - otp_obj.attempts
                    messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
                    
            except EmailOTP.DoesNotExist:
                messages.error(request, 'OTP not found. Please request a new one.')
                return redirect('register_step1_email')
    else:
        form = OTPForm()
    
    return render(request, 'core/register_step2_verify_otp.html', {'form': form, 'email': email})


def register_step3_create_account(request):
    """Step 3: Create account (original register view) - STRICTLY REQUIRES EMAIL VERIFICATION"""
    email = request.session.get('registration_email')
    otp_verified = request.session.get('otp_verified')
    
    # STRICT EMAIL VERIFICATION - No exceptions!
    if not email or not otp_verified:
        messages.error(request, 'Email verification is REQUIRED. Please complete the registration process.')
        return redirect('register_step1_email')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # STRICT: Email must match verified email
            if form.cleaned_data.get('email') != email:
                messages.error(request, 'Email must match the verified email. Registration failed.')
                return render(request, 'core/register_step3_create_account.html', {'form': form, 'email': email})
            
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # CLEAN UP: Remove OTP and session data
            EmailOTP.objects.filter(email=email).delete()
            request.session.pop('registration_email', None)
            request.session.pop('otp_verified', None)
            
            messages.success(request, 'Registration successful! Your email has been verified. Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm(initial={'email': email})
    
    return render(request, 'core/register_step3_create_account.html', {'form': form, 'email': email})
