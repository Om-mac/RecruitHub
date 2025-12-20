from django import forms
from django.contrib.auth.models import User
from .models import Document, Note, UserProfile, HRProfile

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
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match')
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
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match')
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

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Note Content', 'rows': 5}),
        }
