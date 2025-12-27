from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Document, Note, UserProfile, HRProfile
from bleach import clean
from .file_validators import validate_resume_file, validate_profile_photo, validate_document_file
import re

# XSS Protection helper function
def sanitize_input(value):
    """Sanitize user input to prevent XSS attacks"""
    if not value:
        return value
    # Allow only plain text, remove all HTML/JavaScript
    return clean(str(value).strip(), tags=[], strip=True)


def validate_username_format(username):
    """Validate username format - alphanumeric and underscore only"""
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,29}$', username):
        raise forms.ValidationError(
            'Username must start with a letter, contain only letters, numbers, and underscores, '
            'and be 3-30 characters long.'
        )
    return username


def validate_phone_format(phone):
    """Validate phone number format"""
    if not phone:
        return phone
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Must be 10-15 digits, optionally starting with +
    if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
        raise forms.ValidationError('Enter a valid phone number (10-15 digits).')
    return cleaned


def validate_password_strength(password):
    """
    Validate password meets security requirements:
    - At least 10 characters (matches settings.py)
    - Uses Django's built-in validators
    """
    if not password:
        raise forms.ValidationError('Password is required.')
    
    # Use Django's password validators (defined in settings.py)
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise forms.ValidationError(list(e.messages))
    
    return password


    
    def clean_username(self):
        username = sanitize_input(self.cleaned_data.get('username'))
        if not username:
            raise forms.ValidationError('Username is required.')
        # Validate username format
        validate_username_format(username)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username already exists. Please choose another.')
        return username
    
    def clean_email(self):
        email = sanitize_input(self.cleaned_data.get('email'))
        if not email:
            raise forms.ValidationError('Email is required.')
        # Normalize email to lowercase
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_first_name(self):
        first_name = sanitize_input(self.cleaned_data.get('first_name'))
        if not first_name:
            raise forms.ValidationError('First name is required.')
        return first_name
    
    def clean_last_name(self):
        last_name = sanitize_input(self.cleaned_data.get('last_name'))
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        return last_name
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Use Django's password validators (includes length, complexity, common password checks)
        return validate_password_strength(password)
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class HRLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class HRRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }
    
    def clean_username(self):
        username = sanitize_input(self.cleaned_data.get('username'))
        if not username:
            raise forms.ValidationError('Username is required.')
        # Validate username format
        validate_username_format(username)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username already exists. Please choose another.')
        return username
    
    def clean_email(self):
        email = sanitize_input(self.cleaned_data.get('email'))
        if not email:
            raise forms.ValidationError('Email is required.')
        # Normalize email to lowercase
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_first_name(self):
        first_name = sanitize_input(self.cleaned_data.get('first_name'))
        if not first_name:
            raise forms.ValidationError('First name is required.')
        return first_name
    
    def clean_last_name(self):
        last_name = sanitize_input(self.cleaned_data.get('last_name'))
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        return last_name
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Use Django's password validators
        return validate_password_strength(password)
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class HRProfileForm(forms.ModelForm):
    class Meta:
        model = HRProfile
        fields = ['company_name', 'designation', 'department', 'admin_notes']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name', 'maxlength': '255'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation', 'maxlength': '100'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department', 'maxlength': '100'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any notes or message for admin (optional)', 'rows': 4, 'maxlength': '1000'}),
        }
    
    def clean_company_name(self):
        return sanitize_input(self.cleaned_data.get('company_name'))
    
    def clean_designation(self):
        return sanitize_input(self.cleaned_data.get('designation'))
    
    def clean_department(self):
        return sanitize_input(self.cleaned_data.get('department'))
    
    def clean_admin_notes(self):
        return sanitize_input(self.cleaned_data.get('admin_notes'))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['middle_name', 'phone', 'date_of_birth', 'gender', 'address', 'city', 'state', 'pincode', 'profile_photo', 'resume', 'college_name', 'branch', 'degree', 'specialization', 'cgpa', 'year_of_study', 'admission_year', 'backlogs', 'current_backlogs', 'certifications_links', 'skills', 'experience', 'bio', 'github_username', 'linkedin_username', 'hackerrank_username', 'other_platforms']
        widgets = {
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College Name'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch (CSE, ECE, etc.)'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'CGPA', 'step': '0.01'}),
            'year_of_study': forms.Select(attrs={'class': 'form-control'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Admission Year (e.g., 2022)', 'type': 'number', 'min': '1990', 'max': '2100'}),
            'backlogs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Backlogs', 'type': 'number', 'min': '0'}),
            'current_backlogs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Backlogs', 'type': 'number', 'min': '0'}),
            'certifications_links': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Certification Links (one per line)', 'rows': 3}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Skills (comma separated)', 'rows': 3}),
            'github_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Username'}),
            'linkedin_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Username'}),
            'hackerrank_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HackerRank Username'}),
            'other_platforms': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Other Platforms (e.g., Codeforces: username)', 'rows': 3}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Work Experience', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bio / About Me', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png',
                'title': 'JPG or PNG image, max 1 MB'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf',
                'title': 'PDF file, max 5 MB'
            }),
        }
    
    def clean_profile_photo(self):
        """Validate profile photo file"""
        file = self.cleaned_data.get('profile_photo')
        if file:
            validate_profile_photo(file)
        return file
    
    def clean_resume(self):
        """Validate resume file"""
        file = self.cleaned_data.get('resume')
        if file:
            validate_resume_file(file)
        return file
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        return validate_phone_format(phone) if phone else phone
    
    # XSS sanitization for all text fields
    def clean_middle_name(self):
        return sanitize_input(self.cleaned_data.get('middle_name'))
    
    def clean_address(self):
        return sanitize_input(self.cleaned_data.get('address'))
    
    def clean_city(self):
        return sanitize_input(self.cleaned_data.get('city'))
    
    def clean_state(self):
        return sanitize_input(self.cleaned_data.get('state'))
    
    def clean_pincode(self):
        pincode = sanitize_input(self.cleaned_data.get('pincode'))
        if pincode and not re.match(r'^[0-9]{5,10}$', pincode):
            raise forms.ValidationError('Enter a valid pincode (5-10 digits).')
        return pincode
    
    def clean_college_name(self):
        return sanitize_input(self.cleaned_data.get('college_name'))
    
    def clean_branch(self):
        return sanitize_input(self.cleaned_data.get('branch'))
    
    def clean_degree(self):
        return sanitize_input(self.cleaned_data.get('degree'))
    
    def clean_specialization(self):
        return sanitize_input(self.cleaned_data.get('specialization'))
    
    def clean_certifications_links(self):
        return sanitize_input(self.cleaned_data.get('certifications_links'))
    
    def clean_skills(self):
        return sanitize_input(self.cleaned_data.get('skills'))
    
    def clean_github_username(self):
        username = sanitize_input(self.cleaned_data.get('github_username'))
        if username and not re.match(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$', username):
            raise forms.ValidationError('Enter a valid GitHub username.')
        return username
    
    def clean_linkedin_username(self):
        return sanitize_input(self.cleaned_data.get('linkedin_username'))
    
    def clean_hackerrank_username(self):
        return sanitize_input(self.cleaned_data.get('hackerrank_username'))
    
    def clean_other_platforms(self):
        return sanitize_input(self.cleaned_data.get('other_platforms'))
    
    def clean_experience(self):
        return sanitize_input(self.cleaned_data.get('experience'))
    
    def clean_bio(self):
        return sanitize_input(self.cleaned_data.get('bio'))

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        if password1:
            validate_password_strength(password1)
        return cleaned_data

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
            'autocomplete': 'current-password'
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError('New passwords do not match')
        if cleaned_data.get('new_password1'):
            validate_password_strength(cleaned_data.get('new_password1'))
        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf,image/jpeg,image/png',
                'title': 'PDF, JPG, or PNG file - max 5 MB'
            }),
        }
    
    def clean_file(self):
        """Validate document file"""
        file = self.cleaned_data.get('file')
        if file:
            validate_document_file(file)
        return file
    
    def clean_title(self):
        """Sanitize document title to prevent XSS"""
        return sanitize_input(self.cleaned_data.get('title'))

class OTPForm(forms.Form):
    """Form for OTP verification"""
    otp = forms.CharField(
        label='Enter OTP',
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'autocomplete': 'off',
            'inputmode': 'numeric'
        })
    )
    
    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError('OTP must be 6 digits')
        return otp

class EmailOTPForm(forms.Form):
    """Form for requesting OTP via email"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note Title', 'maxlength': '200'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Note Content', 'rows': 5, 'maxlength': '10000'}),
        }
    
    def clean_title(self):
        """Sanitize note title to prevent XSS"""
        return sanitize_input(self.cleaned_data.get('title'))
    
    def clean_content(self):
        """Sanitize note content to prevent XSS"""
        return sanitize_input(self.cleaned_data.get('content'))
    
class UserRegistrationForm:
    class UserRegistrationForm(forms.ModelForm):
        password = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        )
        password_confirm = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
        )

        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
                'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
                'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            }

        def clean_username(self):
            username = sanitize_input(self.cleaned_data.get('username'))
            if not username:
                raise forms.ValidationError('Username is required.')
            validate_username_format(username)
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('This username already exists. Please choose another.')
            return username

        def clean_email(self):
            email = sanitize_input(self.cleaned_data.get('email'))
            if not email:
                raise forms.ValidationError('Email is required.')
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already registered.')
            return email

        def clean_first_name(self):
            first_name = sanitize_input(self.cleaned_data.get('first_name'))
            if not first_name:
                raise forms.ValidationError('First name is required.')
            return first_name

        def clean_last_name(self):
            last_name = sanitize_input(self.cleaned_data.get('last_name'))
            if not last_name:
                raise forms.ValidationError('Last name is required.')
            return last_name

        def clean_password(self):
            password = self.cleaned_data.get('password')
            return validate_password_strength(password)

        def clean(self):
            cleaned_data = super().clean()
            if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
                raise forms.ValidationError('Passwords do not match.')
            return cleaned_data