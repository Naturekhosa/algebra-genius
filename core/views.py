from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm, CustomLoginForm
from .decorators import student_required, teacher_required


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'core/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        return '/redirect-dashboard/'


@login_required
def redirect_dashboard(request):
    if request.user.role == 'STUDENT':
        return redirect('student_dashboard')
    elif request.user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('login')


@login_required
@student_required
def student_dashboard(request):
    return render(request, 'core/student_dashboard.html')


@login_required
@teacher_required
def teacher_dashboard(request):
    return render(request, 'core/teacher_dashboard.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')