from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentRegistrationForm, CustomLoginForm, TopicForm
from .decorators import student_required, teacher_required
from .models import Topic, Lesson, Quiz, Attempt, Option, CustomUser

# --- Public Views ---

def home(request):
    """Renders the main landing page[cite: 208]."""
    return render(request, 'core/home.html')

def register(request):
    """Handles student account creation[cite: 29, 75, 90]."""
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
    """Handles secure user login[cite: 30, 83]."""
    template_name = 'core/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        return '/redirect-dashboard/'

# --- Access Control & Routing ---

@login_required
def redirect_dashboard(request):
    """Redirects users to their specific dashboard based on role[cite: 158]."""
    if request.user.role == 'STUDENT':
        return redirect('student_dashboard')
    elif request.user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('login')

# --- Student Learning Experience ---

@login_required
@student_required
def student_dashboard(request):
    """Displays topics and lessons available to the student[cite: 35, 77, 169]."""
    # Fetch all topics and their related lessons [cite: 104]
    topics = Topic.objects.all().prefetch_related('lessons')

    # NEW: Fetch only THIS student's attempts, ordered by most recent
    my_attempts = Attempt.objects.filter(student=request.user).order_by('-date_taken')[:5]
    
    return render(request, 'core/student_dashboard.html', {
        'topics': topics,
        'my_attempts': my_attempts  # Send attempts to the template
    })

@login_required
@student_required
def lesson_detail(request, pk):
    """Displays content for a specific lesson and links to the related quiz[cite: 78, 105]."""
    # Retrieve the specific lesson [cite: 104]
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Find the quiz associated with this lesson's topic [cite: 266]
    quiz = Quiz.objects.filter(topic=lesson.topic).first()
    
    return render(request, 'core/lesson_detail.html', {
        'lesson': lesson,
        'quiz': quiz 
    })

@login_required
@student_required
def take_quiz(request, pk):
    """Handles quiz attempts and automatic marking[cite: 39, 79, 112]."""
    quiz = get_object_or_404(Quiz, pk=pk)
    
    if request.method == 'POST':
        score = 0
        questions = quiz.questions.all()
        total_questions = questions.count()
        
        for question in questions:
            # Retrieve the student's selected option ID from the form [cite: 61, 112]
            selected_option_id = request.POST.get(f'question_{question.id}')
            
            if selected_option_id:
                selected_option = get_object_or_404(Option, id=selected_option_id)
                # Check if the selection is correct for auto-marking [cite: 41, 87, 113]
                if selected_option.is_correct:
                    score += 1
        
        # Calculate percentage score [cite: 42]
        final_score = int((score / total_questions) * 100) if total_questions > 0 else 0
        
        # Store the attempt results in the database [cite: 45, 60, 114]
        Attempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=final_score
        )
        
        return redirect('student_dashboard')

    return render(request, 'core/take_quiz.html', {'quiz': quiz})

@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    
    if request.method == 'POST':
        score = 0
        questions = quiz.questions.all()
        total_questions = questions.count()
        
        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = get_object_or_404(Option, id=selected_option_id)
                if selected_option.is_correct:
                    score += 1
        
        final_score = int((score / total_questions) * 100) if total_questions > 0 else 0
        
        # Save the attempt
        Attempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=final_score
        )
        
        # NEW: Instead of redirecting, show the results page immediately
        return render(request, 'core/quiz_results.html', {
            'quiz': quiz,
            'score': final_score,
            'correct_count': score,
            'total_questions': total_questions
        })

    return render(request, 'core/take_quiz.html', {'quiz': quiz})

# --- Teacher & Management Views ---

@login_required
@teacher_required
def teacher_dashboard(request):
    """Renders the teacher interface for monitoring performance[cite: 26, 88, 129]."""
    return render(request, 'core/teacher_dashboard.html')

@login_required
@teacher_required
def teacher_dashboard(request):
    # Stats for the top boxes (matching your wireframe)
    student_count = CustomUser.objects.filter(role='STUDENT').count()
    quiz_count = Quiz.objects.count()
    lesson_count = Lesson.objects.count()
    
    # Recent activity as requested
    recent_attempts = Attempt.objects.select_related('student', 'quiz').order_by('-date_taken')[:5]
    
    return render(request, 'core/teacher_dashboard.html', {
        'student_count': student_count,
        'quiz_count': quiz_count,
        'lesson_count': lesson_count,
        'recent_attempts': recent_attempts,
    })

@login_required
@teacher_required
def manage_topics(request):
    topics = Topic.objects.all()
    
    # Handle the "Add New Topic" form submission
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_topics')
    else:
        form = TopicForm()
        
    return render(request, 'core/manage_topics.html', {
        'topics': topics,
        'form': form
    })

@login_required
@teacher_required
def edit_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('manage_topics')
    else:
        form = TopicForm(instance=topic)
    return render(request, 'core/edit_topic.html', {'form': form, 'topic': topic})

@login_required
@teacher_required
def delete_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        topic.delete()
        return redirect('manage_topics')
    return render(request, 'core/delete_topic.html', {'topic': topic})

@login_required
def logout_view(request):
    """Logs the user out and returns to login page[cite: 30]."""
    logout(request)
    return redirect('login')

