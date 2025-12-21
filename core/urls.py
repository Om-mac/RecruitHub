from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Registration with OTP
    path('register_step1/', views.register_step1_email, name='register_step1_email'),
    path('register_step2/', views.register_step2_verify_otp, name='register_step2_verify_otp'),
    path('register_step3/', views.register_step3_create_account, name='register_step3_create_account'),
    path('register/', views.register, name='register'),  # Keep old register for backward compatibility
    
    path('profile/', views.profile, name='profile'),
    path('upload/', views.upload_document, name='upload_document'),
    path('add_note/', views.add_note, name='add_note'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('note/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    
    # Password reset URLs
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Change password URLs
    path('change_password/', views.change_password, name='change_password'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    
    # HR URLs
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/register/', views.hr_register, name='hr_register'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/student/<int:user_id>/', views.student_detail, name='student_detail'),
    path('hr/logout/', views.hr_logout, name='hr_logout'),
]
