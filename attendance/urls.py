from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
 
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty_attendance/<int:faculty_id>/', views.faculty_attendance, name='faculty_attendance'),
    path('add_student/', views.add_student, name='add_student'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('add_faculty/', views.add_faculty, name='add_faculty'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('edit_teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('edit_faculty/<int:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('delete_faculty/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('home/', views.home, name='home'),
     ] 
