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
    
    # Password reset URLs - OTP based (3-step process)
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset_verify_otp/', views.password_reset_verify_otp, name='password_reset_verify_otp'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    
    # Change password URLs
    path('change_password/', views.change_password, name='change_password'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    
    # HR Registration with OTP (3-step process)
    path('hr/register/', views.hr_register, name='hr_register'),
    path('hr/register_step1/', views.hr_register_step1_email, name='hr_register_step1_email'),
    path('hr/register_step2/', views.hr_register_step2_verify_otp, name='hr_register_step2_verify_otp'),
    path('hr/register_step3/', views.hr_register_step3_create_account, name='hr_register_step3_create_account'),
    
    # HR URLs
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/student/<int:user_id>/', views.student_detail, name='student_detail'),
    path('hr/logout/', views.hr_logout, name='hr_logout'),
    
    # Admin utility
    path('admin/create-test-users/', views.create_test_users, name='create_test_users'),
]
