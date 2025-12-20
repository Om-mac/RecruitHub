from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .models import Document, Note, UserProfile, HRProfile
from .forms import DocumentForm, NoteForm, UserRegistrationForm, UserProfileForm, HRLoginForm, HRRegistrationForm, HRProfileForm

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
