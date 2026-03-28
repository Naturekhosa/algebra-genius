from django.urls import path
from .views import (
    home,
    register,
    CustomLoginView,
    redirect_dashboard,
    student_dashboard,
    teacher_dashboard,
    logout_view,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('redirect-dashboard/', redirect_dashboard, name='redirect_dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
]