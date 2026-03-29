from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Topic, Lesson, Quiz, Question, Option, Attempt

# --- Keep your existing User Admin logic ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_active')

# --- Register Math Content Models ---

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order')
    list_filter = ('topic',)
    search_fields = ('title', 'content')

# --- Quiz Management for Teachers ---

class OptionInline(admin.TabularInline):
    """Allows adding answer options directly inside the Question page"""
    model = Option
    extra = 4  # Provides 4 blank slots for multiple choice options

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('text', 'quiz')
    list_filter = ('quiz',)

admin.site.register(Quiz)
admin.site.register(Attempt)