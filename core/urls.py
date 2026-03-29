from django.urls import path
from .views import (
    home,
    register,
    CustomLoginView,
    redirect_dashboard,
    student_dashboard,
    teacher_dashboard,
    logout_view,
    lesson_detail,  # New: Logic to view a specific lesson
    take_quiz       # New: Logic to take a specific quiz
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('redirect-dashboard/', redirect_dashboard, name='redirect_dashboard'),
    
    # Dashboard Routes
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),

    # Content Routes (Crucial for Functional Requirements 3.2 and 3.3)
    path('lesson/<int:pk>/', lesson_detail, name='lesson_detail'), # [cite: 35]
    path('quiz/<int:pk>/', take_quiz, name='take_quiz'), 
              
    path('quiz/<int:pk>/', take_quiz, name='take_quiz'),                    # 
]