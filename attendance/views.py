from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Student, Teacher, Attendance, Faculty
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse

import requests
import ipaddress
from geopy.distance import geodesic
from .models import Attendance

@login_required
def mark_attendance(request):
    if request.method == 'POST':
        user_ip = request.META['REMOTE_ADDR']
        try:
            ipaddress.ip_address(user_ip)
        except ValueError:
            messages.error(request, 'Invalid IP address.')
            return redirect('home')

        try:
            response = requests.get(f'http://ip-api.com/json/{user_ip}').json()
            if response['status'] == 'fail':
                raise ValueError('Failed to get location')
            user_location = {'lat': response['lat'], 'lng': response['lon']}
        except (requests.RequestException, ValueError, KeyError) as e:
            messages.error(request, f'Error getting location: {e}')
            return redirect('home')

        college_location = {'lat': 42.85747034165005, 'lng': 74.59859944086045}
        distance = calculate_distance(user_location, college_location)
        if distance <= 0.5:
            now = timezone.now()
            status = 'present' if now.time() < timezone.time(10, 0) else 'late'
            Attendance.objects.create(user=request.user, status=status)
            messages.success(request, f'Attendance marked as {status}')
        else:
            messages.error(request, 'You are not within the college bounds.')
    return redirect('home')

def calculate_distance(user_location, college_location):
    return geodesic(user_location, college_location).kilometers

@login_required
def edit_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        student.user.username = request.POST['username']
        student.user.save()
        student.faculty = Faculty.objects.get(id=request.POST['faculty'])
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('admin_dashboard')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/edit_student.html', {
        'student': student,
        'faculties': faculties,
    })

@login_required
def delete_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = Student.objects.get(id=student_id)
    student.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('admin_dashboard')

@login_required
def edit_teacher(request, teacher_id):
    if not request.user.is_staff:
        return redirect('home')
    teacher = Teacher.objects.get(id=teacher_id)
    if request.method == 'POST':
        teacher.user.username = request.POST['username']
        teacher.user.save()
        teacher.faculty = Faculty.objects.get(id=request.POST['faculty'])
        teacher.save()
        messages.success(request, 'Teacher updated successfully.')
        return redirect('admin_dashboard')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/edit_teacher.html', {
        'teacher': teacher,
        'faculties': faculties
    })

@login_required
def delete_teacher(request, teacher_id):
    if not request.user.is_staff:
        return redirect('home')
    teacher = Teacher.objects.get(id=teacher_id)
    teacher.delete()
    messages.success(request, 'Teacher deleted successfully.')
    return redirect('admin_dashboard')

@login_required
def edit_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect('home')
    faculty = Faculty.objects.get(id=faculty_id)
    if request.method == 'POST':
        faculty.name = request.POST['name']
        faculty.save()
        messages.success(request, 'Faculty updated successfully.')
        return redirect('admin_dashboard')
    return render(request, 'attendance/edit_faculty.html', {
        'faculty': faculty
    })

@login_required
def delete_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect('home')
    faculty = Faculty.objects.get(id=faculty_id)
    faculty.delete()
    messages.success(request, 'Faculty deleted successfully.')
    return redirect('admin_dashboard')

def get_attendance_stats(faculty):
    students = Student.objects.filter(faculty=faculty)
    attendance_stats = {}
    for student in students:
        attendance_records = Attendance.objects.filter(user=student.user).order_by('-date')
        attendance_stats[student.user.username] = {
            'present': attendance_records.filter(status='present').count(),
            'late': attendance_records.filter(status='late').count(),
            'absent': attendance_records.filter(status='absent').count()
        }
    return attendance_stats

@login_required
def faculty_attendance(request, faculty_id):
    if not request.user.is_staff:
        return redirect('home')
    faculty = Faculty.objects.get(id=faculty_id)
    students = Student.objects.filter(faculty=faculty)
    attendance_stats = get_attendance_stats(faculty)
    return render(request, 'attendance/faculty_attendance.html', {
        'faculty': faculty,
        'students': students,
        'attendance_stats': attendance_stats
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/admin_dashboard.html', {'faculties': faculties})

@login_required
def add_student(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        faculty_id = request.POST['faculty']
        try:
            user = User.objects.create_user(username=username, password=password)
            faculty = Faculty.objects.get(id=faculty_id)
            Student.objects.create(user=user, faculty=faculty)
            messages.success(request, 'Student added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding student: {e}')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/add_student.html', {'faculties': faculties})

@login_required
def add_teacher(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        faculty_id = request.POST['faculty']
        try:
            user = User.objects.create_user(username=username, password=password)
            faculty = Faculty.objects.get(id=faculty_id)
            Teacher.objects.create(user=user, faculty=faculty)
            messages.success(request, 'Teacher added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding teacher: {e}')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/add_teacher.html', {'faculties': faculties})

@login_required
def add_faculty(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        name = request.POST['name']
        try:
            Faculty.objects.create(name=name)
            messages.success(request, 'Faculty added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding faculty: {e}')
    return render(request, 'attendance/add_faculty.html', {})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'attendance/login.html')

@login_required
def home(request):
    if hasattr(request.user, 'student'):
        return render(request, 'attendance/student_home.html')
    elif hasattr(request.user, 'teacher'):
        return render(request, 'attendance/teacher_home.html')
    elif request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return render(request, 'attendance/error.html', {'message': 'User type not recognized'})
