from django.contrib import admin
from .models import StudentProfile, CompanyProfile, Job, Application, Resource

admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Resource)


# Register your models here.
