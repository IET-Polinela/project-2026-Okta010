from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Definisikan CustomUser terlebih dahulu
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# 2. Baru definisikan model Report di bawahnya (Cukup SATU saja)
class Report(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('REPORTED', 'Reported'),
        ('VERIFIED', 'Verified'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    # Menggunakan settings.AUTH_USER_MODEL agar fleksibel dan aman
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reports',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=250)
    category = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='DRAFT'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title