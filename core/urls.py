from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('upload/', views.upload_document, name='upload_document'),
    path('add_note/', views.add_note, name='add_note'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('note/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    
    # HR URLs
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/register/', views.hr_register, name='hr_register'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/student/<int:user_id>/', views.student_detail, name='student_detail'),
    path('hr/logout/', views.hr_logout, name='hr_logout'),
]
