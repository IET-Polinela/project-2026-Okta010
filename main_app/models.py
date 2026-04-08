from django.db import models

class Report(models.Model):
    # 1. TAMBAHKAN variabel pilihan status di sini [cite: 151-156]
    STATUS_CHOICES = [
        ('REPORTED', 'Reported'),
        ('VERIFIED', 'Verified'),
        ('IN PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=200)

    # 2. PERBARUI field status dengan menambahkan parameter 'choices' [cite: 163-166]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,  # Menghubungkan ke STATUS_CHOICES
        default='REPORTED'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title