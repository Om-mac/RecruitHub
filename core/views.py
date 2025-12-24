from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
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
from .models import Document, Note, UserProfile, HRProfile, EmailOTP, IPRateLimit
from .forms import DocumentForm, NoteForm, UserRegistrationForm, UserProfileForm, HRLoginForm, HRRegistrationForm, HRProfileForm, PasswordResetForm, SetPasswordForm, ChangePasswordForm, OTPForm, EmailOTPForm
from .utils import get_client_ip

User = get_user_model()
logger = logging.getLogger('core')


class StudentLoginView(LoginView):
    """Custom login view that blocks HR and staff accounts from logging in as students"""
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Override to check if user is HR/staff before logging in"""
        user = form.get_user()
        
        # BLOCK: HR accounts, staff, and superusers from student login
        if user.is_staff or user.is_superuser or hasattr(user, 'hr_profile'):
            messages.error(self.request, '❌ HR and Staff accounts must use the HR login page. Please login at /hr/login/')
            return redirect('login')
        
        # Allow normal students to login
        return super().form_valid(form)


def send_hr_approval_email(hr_profile, approval_token):
    """
    Send HR account approval request email to admin
    """
    try:
        logger.info("=" * 80)
        logger.info("🔔 [STEP 1] send_hr_approval_email() CALLED")
        logger.info(f"   HR Profile ID: {hr_profile.id}")
        logger.info(f"   User: {hr_profile.user.username}")
        logger.info("=" * 80)
        
        admin_email = getattr(settings, 'HR_APPROVAL_EMAIL', 'omtapdiya75@gmail.com')
        user = hr_profile.user
        
        logger.info(f"[STEP 2] Email Configuration:")
        logger.info(f"   Admin Email: {admin_email}")
        logger.info(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"   Backend: {settings.EMAIL_BACKEND}")
        
        # Generate approval and rejection URLs
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        approval_url = f"{site_url}/admin/approve-hr/{approval_token}/"
        rejection_url = f"{site_url}/admin/reject-hr/{approval_token}/"
        
        logger.info(f"[STEP 3] URLs Generated:")
        logger.info(f"   Site URL: {site_url}")
        logger.info(f"   Approval Token: {approval_token[:20]}... (truncated)")
        logger.info(f"   Approval URL: {approval_url}")
        logger.info(f"   Rejection URL: {rejection_url}")
        
        subject = f"New HR Registration - {user.username} from {hr_profile.company_name}"
        
        message = f"""
New HR Account Approval Request

Username: {user.username}
Name: {user.first_name} {user.last_name}
Email: {user.email}
Company: {hr_profile.company_name}
Designation: {hr_profile.designation}
Department: {hr_profile.department}

Please review and approve or reject this account:

APPROVE: {approval_url}
REJECT: {rejection_url}

This is an automated email from RecruitHub Admin Panel.
        """
        
        logger.info(f"[STEP 4] Email Content Prepared:")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   To: {admin_email}")
        logger.info(f"   From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"   Message Length: {len(message)} characters")
        
        # Send using Django's send_mail
        logger.info(f"[STEP 5] Calling Django send_mail()...")
        
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
        
        logger.info(f"[STEP 6] send_mail() RETURNED: {result}")
        
        if result:
            logger.info(f"✅ SUCCESS: HR approval email sent successfully!")
            logger.info(f"   User: {user.username}")
            logger.info(f"   To: {admin_email}")
            logger.info(f"   Subject: {subject}")
            logger.info("=" * 80)
        else:
            logger.error(f"❌ ERROR: send_mail() returned 0 (no emails sent)")
            logger.error(f"   User: {user.username}")
            logger.error(f"   To: {admin_email}")
            logger.error("=" * 80)
            
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ EXCEPTION: Failed to send HR approval email")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error(f"   Exception Message: {str(e)}")
        logger.error(f"   User: {hr_profile.user.username if hr_profile else 'N/A'}")
        logger.error("=" * 80)
        logger.error("Full Traceback:")
        logger.error("", exc_info=True)

def home(request):
    """Home page - redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def register(request):
    """
    OLD REGISTER ENDPOINT - REDIRECTS TO OTP-BASED REGISTRATION
    All registrations MUST go through email verification with OTP
    No exceptions allowed!
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # ENFORCE: All registrations must use OTP verification flow
    messages.info(request, 'Please register using our secure email verification process.')
    return redirect('register_step1_email')

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
                    # Check if HR account is approved
                    if not user.hr_profile.is_approved:
                        messages.error(request, 'Your HR account is pending admin approval. Please wait for verification.')
                        return redirect('hr_login')
                    
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
    """
    HR Registration - Now requires email verification with OTP
    Step 1 of 3-step HR registration process
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'hr_profile'):
            return redirect('hr_dashboard')
        else:
            return redirect('dashboard')
    
    # ENFORCE: All HR registrations must use OTP verification flow
    messages.info(request, 'Please register using our secure email verification process.')
    return redirect('hr_register_step1_email')


def hr_register_step1_email(request):
    """HR Registration Step 1: Enter email"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'hr_profile'):
            return redirect('hr_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if HR already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'core/hr_register_step1_email.html', {'form': form})
            
            # Check rate limiting for OTP requests
            try:
                email_otp = EmailOTP.objects.get(email=email)
                
                # Check if locked out due to failed attempts
                if email_otp.is_locked_out():
                    minutes = EmailOTP.ATTEMPT_LOCKOUT_MINUTES
                    messages.error(request, f'Too many failed attempts. Please try again in {minutes} minutes.')
                    return render(request, 'core/hr_register_step1_email.html', {'form': form})
                
                # Check rate limit for requesting new OTP
                can_request, wait_seconds = email_otp.can_request_otp()
                if not can_request:
                    messages.warning(request, f'Please wait {wait_seconds} seconds before requesting a new OTP.')
                    return render(request, 'core/hr_register_step1_email.html', {'form': form})
                
                # Check hourly request limit
                hourly_requests = email_otp.get_hourly_request_count()
                if hourly_requests >= EmailOTP.MAX_ATTEMPTS_PER_HOUR:
                    messages.error(request, f'You have requested {hourly_requests} OTPs in the last hour. Please try again later.')
                    return render(request, 'core/hr_register_step1_email.html', {'form': form})
                
            except EmailOTP.DoesNotExist:
                pass  # New email, no rate limiting check needed
            
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Save OTP with rate limiting record
            EmailOTP.objects.filter(email=email).delete()
            email_otp = EmailOTP.objects.create(email=email, otp=otp)
            email_otp.record_otp_request()
            
            # Send OTP email in background
            send_otp_email(email, otp)
            
            # Store email in session
            request.session['hr_registration_email'] = email
            request.session['hr_otp_verified'] = False
            
            messages.success(request, f'OTP sent to {email}')
            return redirect('hr_register_step2_verify_otp')
        else:
            messages.error(request, 'Please enter a valid email.')
    else:
        form = EmailOTPForm()
    
    return render(request, 'core/hr_register_step1_email.html', {'form': form})


def hr_register_step2_verify_otp(request):
    """HR Registration Step 2: Verify OTP - Protected with IP rate limiting"""
    email = request.session.get('hr_registration_email')
    
    if not email:
        messages.error(request, 'Please start from email entry.')
        return redirect('hr_register_step1_email')
    
    # Get client IP for rate limiting
    client_ip = get_client_ip(request)
    
    if request.method == 'POST':
        # Check IP rate limiting (3 attempts per minute)
        ip_limiter = IPRateLimit.get_or_create_for_ip(client_ip, endpoint='otp_verify')
        is_blocked, remaining_attempts, wait_seconds = ip_limiter.check_rate_limit()
        
        if is_blocked:
            messages.error(request, f'Too many verification attempts from your IP. Please try again in {wait_seconds // 60} minutes.')
            return render(request, 'core/hr_register_step2_verify_otp.html', {'form': OTPForm(), 'email': email})
        
        # Increment IP attempt counter
        ip_limiter.increment_attempt()
        
        form = OTPForm(request.POST)
        if form.is_valid():
            # Strip whitespace from OTP input
            otp_code = form.cleaned_data['otp'].strip()
            
            # Verify OTP
            try:
                otp_obj = EmailOTP.objects.get(email=email)
                
                # Check if locked out
                if otp_obj.is_locked_out():
                    minutes = EmailOTP.ATTEMPT_LOCKOUT_MINUTES
                    messages.error(request, f'Too many failed attempts. Account locked for {minutes} minutes.')
                    return redirect('hr_register_step1_email')
                
                if otp_obj.is_expired():
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('hr_register_step1_email')
                
                if not otp_obj.is_valid_attempt():
                    messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                    return redirect('hr_register_step1_email')
                
                # Debug: Log OTP verification attempt (without revealing the hash)
                logger.debug(f'Verifying OTP for {email} - Length: {len(otp_code)}')
                
                # Verify hashed OTP
                if otp_obj.verify_otp(otp_code):
                    # Mark as verified, reset failed attempts, and DELETE OTP record (one-time use)
                    otp_obj.reset_failed_attempts()
                    # Reset IP rate limiting on success
                    ip_limiter.reset_for_ip()
                    # Delete OTP record - one-time use only
                    otp_obj.delete()
                    request.session['hr_otp_verified'] = True
                    messages.success(request, 'Email verified! Now create your HR account.')
                    return redirect('hr_register_step3_create_account')
                else:
                    # Invalid OTP - record failed attempt
                    otp_obj.record_failed_attempt()
                    logger.warning(f'Invalid OTP attempt for {email} - Attempts: {otp_obj.failed_attempts}/{EmailOTP.MAX_FAILED_ATTEMPTS}')
                    
                    remaining = EmailOTP.MAX_FAILED_ATTEMPTS - otp_obj.failed_attempts
                    if remaining > 0:
                        messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
                    else:
                        messages.error(request, f'Too many failed attempts. Account locked for {EmailOTP.ATTEMPT_LOCKOUT_MINUTES} minutes.')
                        return redirect('hr_register_step1_email')
                
            except EmailOTP.DoesNotExist:
                messages.error(request, 'OTP not found. Please request a new one.')
                return redirect('hr_register_step1_email')
        else:
            messages.error(request, 'Please enter a valid 6-digit OTP.')
    else:
        form = OTPForm()
    
    return render(request, 'core/hr_register_step2_verify_otp.html', {'form': form, 'email': email})


def hr_register_step3_create_account(request):
    """HR Registration Step 3: Create HR account - STRICTLY REQUIRES EMAIL VERIFICATION"""
    email = request.session.get('hr_registration_email')
    otp_verified = request.session.get('hr_otp_verified')
    
    # STRICT EMAIL VERIFICATION - No exceptions!
    if not email or not otp_verified:
        messages.error(request, 'Email verification is REQUIRED. Please complete the registration process.')
        return redirect('hr_register_step1_email')
    
    if request.method == 'POST':
        user_form = HRRegistrationForm(request.POST)
        if user_form.is_valid():
            # STRICT: Email must match verified email (case-insensitive comparison)
            form_email = user_form.cleaned_data.get('email', '').strip().lower()
            session_email = email.strip().lower() if email else ''
            if form_email != session_email:
                messages.error(request, 'Email must match the verified email. Registration failed.')
                return render(request, 'core/hr_register_step3_create_account.html', {'form': user_form, 'email': email})
            
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.is_staff = True  # Mark as staff member
            user.save()
            
            # Delete any UserProfile that was auto-created (HR users should not have student profiles)
            UserProfile.objects.filter(user=user).delete()
            
            # Create HR Profile (NOT APPROVED by default)
            hr_profile = HRProfile.objects.create(
                user=user,
                company_name=request.POST.get('company_name', ''),
                designation=request.POST.get('designation', ''),
                department=request.POST.get('department', ''),
                is_approved=False
            )
            
            # Generate approval token
            approval_token = hr_profile.generate_approval_token()
            
            # Send approval email to admin
            send_hr_approval_email(hr_profile, approval_token)
            
            # CLEAN UP: Remove OTP and session data
            EmailOTP.objects.filter(email=email).delete()
            request.session.pop('hr_registration_email', None)
            request.session.pop('hr_otp_verified', None)
            
            messages.success(request, 'HR Registration successful! Your email has been verified. Awaiting admin approval.')
            return redirect('hr_login')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = HRRegistrationForm(initial={'email': email})
    
    return render(request, 'core/hr_register_step3_create_account.html', {'form': user_form, 'email': email})


@login_required(login_url='hr_login')
@login_required(login_url='hr_login')
def hr_dashboard(request):
    """HR Dashboard - View and filter students"""
    # Check if user has HR profile
    if not hasattr(request.user, 'hr_profile'):
        messages.error(request, 'You do not have access to HR dashboard.')
        return redirect('dashboard')
    
    # Check if HR account is approved
    if not request.user.hr_profile.is_approved:
        # Show HR's own information and pending approval message
        hr_profile = request.user.hr_profile
        return render(request, 'core/hr_pending_approval.html', {
            'hr_profile': hr_profile,
            'user': request.user
        })
    
    # Get all user profiles (students) - EXCLUDE HR USERS AND ADMIN/STAFF USERS
    # Filter out users who have HR profiles
    hr_user_ids = HRProfile.objects.values_list('user_id', flat=True)
    # Only show actual student profiles (exclude admin, staff, superuser accounts)
    students = UserProfile.objects.select_related('user').exclude(user_id__in=hr_user_ids).exclude(user__is_staff=True).exclude(user__is_superuser=True)
    
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
    
    # Prevent access to admin/staff/superuser profiles
    if student.user.is_staff or student.user.is_superuser:
        messages.error(request, 'You do not have access to this profile.')
        return redirect('hr_dashboard')
    
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
    """Password Reset Step 1: Enter email"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Check rate limiting for OTP requests
                try:
                    email_otp = EmailOTP.objects.get(email=email)
                    
                    # Check if locked out due to failed attempts
                    if email_otp.is_locked_out():
                        minutes = EmailOTP.ATTEMPT_LOCKOUT_MINUTES
                        messages.error(request, f'Too many failed attempts. Please try again in {minutes} minutes.')
                        return render(request, 'core/password_reset.html', {'form': form})
                    
                    # Check rate limit for requesting new OTP
                    can_request, wait_seconds = email_otp.can_request_otp()
                    if not can_request:
                        messages.warning(request, f'Please wait {wait_seconds} seconds before requesting a new OTP.')
                        return render(request, 'core/password_reset.html', {'form': form})
                    
                    # Check hourly request limit
                    hourly_requests = email_otp.get_hourly_request_count()
                    if hourly_requests >= EmailOTP.MAX_ATTEMPTS_PER_HOUR:
                        messages.error(request, f'You have requested {hourly_requests} OTPs in the last hour. Please try again later.')
                        return render(request, 'core/password_reset.html', {'form': form})
                
                except EmailOTP.DoesNotExist:
                    pass  # New OTP request, no rate limiting check needed
                
                # Generate OTP
                otp = ''.join(random.choices(string.digits, k=6))
                
                # Save OTP with rate limiting record
                EmailOTP.objects.filter(email=email).delete()
                email_otp = EmailOTP.objects.create(email=email, otp=otp)
                email_otp.record_otp_request()
                
                # Send OTP email in background
                send_otp_email(email, otp)
                
                # Store email in session
                request.session['password_reset_email'] = email
                request.session['password_reset_otp_verified'] = False
                
                messages.success(request, f'OTP sent to {email}')
                return redirect('password_reset_verify_otp')
            except User.DoesNotExist:
                # For security, show same message even if user doesn't exist
                messages.success(request, 'If an account with this email exists, you will receive an OTP.')
                return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'core/password_reset.html', {'form': form})


def password_reset_verify_otp(request):
    """Password Reset Step 2: Verify OTP - Protected with IP rate limiting"""
    email = request.session.get('password_reset_email')
    
    if not email:
        messages.error(request, 'Please start from email entry.')
        return redirect('password_reset_request')
    
    # Get client IP for rate limiting
    client_ip = get_client_ip(request)
    
    if request.method == 'POST':
        # Check IP rate limiting (3 attempts per minute)
        ip_limiter = IPRateLimit.get_or_create_for_ip(client_ip, endpoint='otp_verify')
        is_blocked, remaining_attempts, wait_seconds = ip_limiter.check_rate_limit()
        
        if is_blocked:
            messages.error(request, f'Too many verification attempts from your IP. Please try again in {wait_seconds // 60} minutes.')
            return render(request, 'core/password_reset_verify_otp.html', {'form': OTPForm(), 'email': email})
        
        # Increment IP attempt counter
        ip_limiter.increment_attempt()
        
        form = OTPForm(request.POST)
        if form.is_valid():
            # Strip whitespace from OTP input
            otp_code = form.cleaned_data['otp'].strip()
            
            # Verify OTP
            try:
                otp_obj = EmailOTP.objects.get(email=email)
                
                # Check if locked out
                if otp_obj.is_locked_out():
                    minutes = EmailOTP.ATTEMPT_LOCKOUT_MINUTES
                    messages.error(request, f'Too many failed attempts. Account locked for {minutes} minutes.')
                    return redirect('password_reset_request')
                
                if otp_obj.is_expired():
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('password_reset_request')
                
                if not otp_obj.is_valid_attempt():
                    messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                    return redirect('password_reset_request')
                
                # Verify hashed OTP
                if otp_obj.verify_otp(otp_code):
                    # Mark as verified and reset failed attempts
                    otp_obj.reset_failed_attempts()
                    # Reset IP rate limiting on success
                    ip_limiter.reset_for_ip()
                    # Delete OTP record - one-time use only
                    otp_obj.delete()
                    request.session['password_reset_otp_verified'] = True
                    messages.success(request, 'OTP verified! Now set your new password.')
                    return redirect('password_reset_confirm')
                else:
                    # Invalid OTP - record failed attempt
                    otp_obj.record_failed_attempt()
                    logger.warning(f'Invalid OTP attempt for password reset - {email} - Attempts: {otp_obj.failed_attempts}/{EmailOTP.MAX_FAILED_ATTEMPTS}')
                    
                    remaining = EmailOTP.MAX_FAILED_ATTEMPTS - otp_obj.failed_attempts
                    if remaining > 0:
                        messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
                    else:
                        messages.error(request, f'Too many failed attempts. Account locked for {EmailOTP.ATTEMPT_LOCKOUT_MINUTES} minutes.')
                        return redirect('password_reset_request')
            
            except EmailOTP.DoesNotExist:
                messages.error(request, 'OTP not found. Please request a new one.')
                return redirect('password_reset_request')
        else:
            messages.error(request, 'Please enter a valid 6-digit OTP.')

    else:
        form = OTPForm()
    
    return render(request, 'core/password_reset_verify_otp.html', {'form': form, 'email': email})


def password_reset_confirm(request):
    """Password Reset Step 3: Set new password - REQUIRES OTP VERIFICATION"""
    email = request.session.get('password_reset_email')
    otp_verified = request.session.get('password_reset_otp_verified')
    
    # STRICT OTP VERIFICATION - No exceptions!
    if not email or not otp_verified:
        messages.error(request, 'OTP verification is REQUIRED. Please complete the password reset process.')
        return redirect('password_reset_request')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            # CLEAN UP: Remove OTP and session data
            EmailOTP.objects.filter(email=email).delete()
            request.session.pop('password_reset_email', None)
            request.session.pop('password_reset_otp_verified', None)
            
            messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SetPasswordForm()
    
    return render(request, 'core/password_reset_confirm.html', {'form': form, 'email': email})


def password_reset_done(request):
    """Show confirmation message after reset request"""
    return render(request, 'core/password_reset_done.html')


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
            # Strip whitespace from OTP input
            otp = form.cleaned_data['otp'].strip()
            
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
                
                # Check if OTP matches (using secure password comparison with hashed OTP)
                if otp_obj.verify_otp(otp):
                    # Mark as verified and proceed to registration
                    otp_obj.reset_failed_attempts()
                    request.session['otp_verified'] = True
                    # Delete OTP record - one-time use only
                    otp_obj.delete()
                    messages.success(request, 'Email verified! Now create your account.')
                    return redirect('register_step3_create_account')
                else:
                    # Increment failed attempts
                    otp_obj.record_failed_attempt()
                    remaining = EmailOTP.MAX_FAILED_ATTEMPTS - otp_obj.failed_attempts
                    if remaining > 0:
                        messages.error(request, f'Invalid OTP. {remaining} attempts remaining.')
                    else:
                        messages.error(request, f'Too many failed attempts. Account locked for {EmailOTP.ATTEMPT_LOCKOUT_MINUTES} minutes.')
                        return redirect('register_step1_email')
                    
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
            # STRICT: Email must match verified email (case-insensitive comparison)
            form_email = form.cleaned_data.get('email', '').strip().lower()
            session_email = email.strip().lower() if email else ''
            if form_email != session_email:
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


def approve_hr_account(request, token):
    """Approve HR account via token link"""
    try:
        hr_profile = HRProfile.objects.get(approval_token=token)
        
        # Check if already approved
        if hr_profile.is_approved:
            messages.warning(request, 'This HR account has already been approved.')
            return redirect('admin:index')
        
        # Approve the account
        hr_profile.is_approved = True
        hr_profile.approved_by = request.user if request.user.is_authenticated and request.user.is_superuser else None
        hr_profile.approved_at = timezone.now()
        hr_profile.save()
        
        # Send approval confirmation email to HR
        send_approval_confirmation_email(hr_profile.user)
        
        messages.success(request, f'HR account {hr_profile.user.username} has been approved successfully.')
        logger.info(f"HR account {hr_profile.user.username} approved by {request.user.username if request.user.is_authenticated else 'anonymous'}")
        
        return redirect('admin:index')
    
    except HRProfile.DoesNotExist:
        messages.error(request, 'Invalid approval token.')
        logger.warning(f"Invalid HR approval token: {token}")
        return redirect('admin:index')


def reject_hr_account(request, token):
    """Reject HR account via token link"""
    try:
        hr_profile = HRProfile.objects.get(approval_token=token)
        
        # Check if already approved
        if hr_profile.is_approved:
            messages.warning(request, 'This HR account has already been approved. Cannot reject approved accounts.')
            return redirect('admin:index')
        
        if request.method == 'POST':
            rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
            
            # Reject the account
            hr_profile.rejection_reason = rejection_reason
            hr_profile.save()
            
            # Delete the user and HR profile
            user = hr_profile.user
            username = user.username
            user.delete()
            
            # Send rejection email
            send_rejection_email(hr_profile.user.email, rejection_reason)
            
            messages.success(request, f'HR account {username} has been rejected and deleted.')
            logger.info(f"HR account {username} rejected. Reason: {rejection_reason}")
            
            return redirect('admin:index')
        
        # GET request - show rejection form
        return render(request, 'core/reject_hr_account.html', {'hr_profile': hr_profile})
    
    except HRProfile.DoesNotExist:
        messages.error(request, 'Invalid rejection token.')
        logger.warning(f"Invalid HR rejection token: {token}")
        return redirect('admin:index')


def send_approval_confirmation_email(user):
    """Send approval confirmation email to HR user"""
    try:
        subject = "Your HR Account Has Been Approved - RecruitHub"
        message = f"""
Hello {user.first_name},

Great news! Your HR account has been approved and is now active.

You can now log in to your HR dashboard using your username and password:
Username: {user.username}

Login URL: {settings.SITE_URL}/hr/login/

If you have any questions, please contact our support team.

Best regards,
RecruitHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"HR approval confirmation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send approval confirmation email to {user.email}: {str(e)}")


def send_rejection_email(email, reason):
    """Send rejection email to HR user"""
    try:
        subject = "Your HR Account Registration - RecruitHub"
        message = f"""
Hello,

Thank you for applying for an HR account with RecruitHub.

Unfortunately, your HR account registration has been rejected.

Reason: {reason}

If you believe this is a mistake or would like more information, please contact our support team.

Best regards,
RecruitHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        logger.info(f"HR rejection email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send rejection email to {email}: {str(e)}")


def send_username_recovery_email(email, username):
    """Send username to user's email for recovery"""
    try:
        subject = "Your RecruitHub Username"
        message = f"""
Hello,

You requested to recover your RecruitHub username.

Your Username: {username}

If you also need to reset your password, please use the 'Forgot Password' option on the login page.

If you did not request this, please ignore this email.

Best regards,
RecruitHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        logger.info(f"✅ Username recovery email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send username recovery email to {email}: {str(e)}", exc_info=True)
        return False


def forgot_username_student(request):
    """Student forgot username view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'core/forgot_username.html')
        
        # Check if email exists for student
        try:
            user = User.objects.get(email=email)
            # Send username recovery email
            if send_username_recovery_email(email, user.username):
                messages.success(request, f'Your username has been sent to {email}. Please check your inbox.')
                return render(request, 'core/username_sent.html', {'email': email, 'user_type': 'Student'})
            else:
                messages.error(request, 'Failed to send email. Please try again later.')
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            messages.success(request, f'If an account with {email} exists, the username has been sent. Please check your inbox.')
            return render(request, 'core/username_sent.html', {'email': email, 'user_type': 'Student'})
        except Exception as e:
            logger.error(f"Error in forgot_username_student: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred. Please try again later.')
    
    return render(request, 'core/forgot_username.html', {'user_type': 'Student'})


def forgot_username_hr(request):
    """HR forgot username view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'core/forgot_username_hr.html')
        
        # Check if email exists for HR
        try:
            user = User.objects.get(email=email)
            # Verify user has HR profile
            hr_profile = HRProfile.objects.filter(user=user).exists()
            if hr_profile:
                if send_username_recovery_email(email, user.username):
                    messages.success(request, f'Your username has been sent to {email}. Please check your inbox.')
                    return render(request, 'core/username_sent.html', {'email': email, 'user_type': 'HR'})
                else:
                    messages.error(request, 'Failed to send email. Please try again later.')
            else:
                # Don't reveal if HR profile exists
                messages.success(request, f'If an HR account with {email} exists, the username has been sent. Please check your inbox.')
                return render(request, 'core/username_sent.html', {'email': email, 'user_type': 'HR'})
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            messages.success(request, f'If an HR account with {email} exists, the username has been sent. Please check your inbox.')
            return render(request, 'core/username_sent.html', {'email': email, 'user_type': 'HR'})
        except Exception as e:
            logger.error(f"Error in forgot_username_hr: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred. Please try again later.')
    
    return render(request, 'core/forgot_username_hr.html', {'user_type': 'HR'})

