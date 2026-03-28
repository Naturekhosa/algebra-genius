from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    STUDENT = 'STUDENT'
    TEACHER = 'TEACHER'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
    ]

    # Override default fields to make them required if needed
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)

    def __str__(self):
        return f"{self.username} ({self.role})"