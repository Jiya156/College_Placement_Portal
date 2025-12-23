from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_user, name='login'),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Company Functions
    path('post-job/', views.post_job, name='post_job'),
    path('update-status/<int:application_id>/', views.update_status, name='update_status'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),


    # Student Functions
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('delete-resume/', views.delete_resume, name='delete_resume'),

    # Admin Functions
    path('upload-resource/', views.upload_resource, name='upload_resource'),
    path('view-applicants/<int:job_id>/', views.view_applicants, name='view_applicants'),
    path('view-students/', views.view_students, name='view_students'),
    path('view-companies/', views.view_companies, name='view_companies'),


    # Resource Management
    path('upload-resource/', views.upload_resource, name='upload_resource'),
    path('resources/', views.resource_list, name='resource_list'),
    path('delete-resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('resources/', views.student_resources, name='student_resources'),



]
