from django import forms
from django.contrib.auth.models import User
from .models import Document, Note, UserProfile, HRProfile
from bleach import clean

# XSS Protection helper function
def sanitize_input(value):
    """Sanitize user input to prevent XSS attacks"""
    if not value:
        return value
    # Allow only plain text, remove all HTML/JavaScript
    return clean(str(value).strip(), tags=[], strip=True)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
    
    def clean_username(self):
        username = sanitize_input(self.cleaned_data.get('username'))
        if not username:
            raise forms.ValidationError('Username is required.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username already exists. Please choose another.')
        # Prevent SQL injection by using ORM (Django handles parameterized queries)
        return username
    
    def clean_email(self):
        email = sanitize_input(self.cleaned_data.get('email'))
        if not email:
            raise forms.ValidationError('Email is required.')
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
        if not password:
            raise forms.ValidationError('Password is required.')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        # Don't sanitize passwords - they may contain special characters
        return password
    
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
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username already exists. Please choose another.')
        return username
    
    def clean_email(self):
        email = sanitize_input(self.cleaned_data.get('email'))
        if not email:
            raise forms.ValidationError('Email is required.')
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
        if not password:
            raise forms.ValidationError('Password is required.')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class HRProfileForm(forms.ModelForm):
    class Meta:
        model = HRProfile
        fields = ['company_name', 'designation', 'department']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
        }

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
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

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
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError('Passwords do not match')
        if len(cleaned_data.get('new_password1', '')) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long')
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
        if len(cleaned_data.get('new_password1', '')) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long')
        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Note Content', 'rows': 5}),
        }
