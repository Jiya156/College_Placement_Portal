from django.db import models
from django.contrib.auth.models import User

# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.CharField(max_length=100)
    cgpa = models.FloatField()
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    placement_status = models.CharField(max_length=50, default='Eligible')

    def __str__(self):
        return self.user.username


# Company Profile
class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


# Job
class Job(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    package = models.CharField(max_length=50)
    details = models.TextField()
    min_cgpa = models.FloatField()
    eligible_branches = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default='Open')

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"


# Application
class Application(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Applied', 'Applied'),
            ('Shortlisted', 'Shortlisted'),
            ('Rejected', 'Rejected'),
            ('Selected', 'Selected')
        ],
        default='Applied'
    )

    def __str__(self):
        return f"{self.student.user.username} → {self.job.title}"


# Resource (uploaded by Admin)
class Resource(models.Model):
    title = models.CharField(max_length=100)
    file_link = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Create your models here.
