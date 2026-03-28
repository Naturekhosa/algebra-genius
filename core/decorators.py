from django.contrib.auth.decorators import user_passes_test


def student_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.role == 'STUDENT',
        login_url='login'
    )(view_func)
    return decorated_view_func


def teacher_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.role == 'TEACHER',
        login_url='login'
    )(view_func)
    return decorated_view_func