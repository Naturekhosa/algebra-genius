from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentRegistrationForm, CustomLoginForm, TopicForm, LessonForm, QuizForm, QuestionForm
from .decorators import student_required, teacher_required
from .models import Topic, Lesson, Quiz, Attempt, Option, CustomUser

# --- Public Views ---

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

# --- Access Control & Routing ---

@login_required
def redirect_dashboard(request):
    if request.user.role == 'STUDENT':
        return redirect('student_dashboard')
    elif request.user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('login')

# --- Student Learning Experience ---

@login_required
@student_required
def student_dashboard(request):
    topics = Topic.objects.all().prefetch_related('lessons')
    my_attempts = Attempt.objects.filter(student=request.user).order_by('-date_taken')[:5]
    
    return render(request, 'core/student_dashboard.html', {
        'topics': topics,
        'my_attempts': my_attempts
    })

@login_required
@student_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    quiz = Quiz.objects.filter(topic=lesson.topic).first()
    return render(request, 'core/lesson_detail.html', {
        'lesson': lesson,
        'quiz': quiz 
    })

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
        
        # Show the results page immediately
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
    # Stats for the top boxes
    student_count = CustomUser.objects.filter(role='STUDENT').count()
    quiz_count = Quiz.objects.count()
    lesson_count = Lesson.objects.count()
    
    # Recent activity
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
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_topics')
    else:
        form = TopicForm()
    return render(request, 'core/manage_topics.html', {'topics': topics, 'form': form})

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
@teacher_required
def manage_lessons(request):
    lessons = Lesson.objects.select_related('topic').all()
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_lessons')
    else:
        form = LessonForm()
    return render(request, 'core/manage_lessons.html', {'lessons': lessons, 'form': form})

@login_required
@teacher_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('manage_lessons')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'core/edit_lesson.html', {'form': form, 'lesson': lesson})

@login_required
@teacher_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        return redirect('manage_lessons')
    return render(request, 'core/delete_lesson.html', {'lesson': lesson})

@login_required
@teacher_required
def manage_quizzes(request):
    quizzes = Quiz.objects.select_related('topic').all()
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_quizzes')
    else:
        form = QuizForm()
    return render(request, 'core/manage_quizzes.html', {'quizzes': quizzes, 'form': form})

@login_required
@teacher_required
def manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('options')

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            # 1. Save the Question shell
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # 2. Grab the 4 options from the POST data
            texts = request.POST.getlist('option_text')
            correct_index = request.POST.get('is_correct') # This will be "0", "1", "2", or "3"

            for i, text in enumerate(texts):
                Option.objects.create(
                    question=question,
                    text=text,
                    is_correct=(str(i) == correct_index)
                )
            
            return redirect('manage_questions', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()

    return render(request, 'core/manage_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'form': question_form
    })
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')