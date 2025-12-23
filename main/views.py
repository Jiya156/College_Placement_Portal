from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StudentProfile, CompanyProfile, Job, Application, Resource
from django.contrib.auth import logout


# -----------------------------------------------
# User Login
# -----------------------------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'studentprofile'):
                return redirect('student_dashboard')
            elif hasattr(user, 'companyprofile'):
                return redirect('company_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# -----------------------------------------------
# Dashboards
# -----------------------------------------------
@login_required
def student_dashboard(request):
    student = StudentProfile.objects.get(user=request.user)
    jobs = Job.objects.all()
    applications = Application.objects.filter(student=student)
    return render(request, 'student_dashboard.html', {
        'student_profile': student,
        'jobs': jobs,
        'applications': applications
    })


@login_required
def company_dashboard(request):
    company = CompanyProfile.objects.get(user=request.user)
    jobs = Job.objects.filter(company=company)
    return render(request, 'company_dashboard.html', {'jobs': jobs})


@login_required
def admin_dashboard(request):
    students = StudentProfile.objects.all()
    companies = CompanyProfile.objects.all()
    return render(request, 'admin_dashboard.html', {
        'students': students,
        'companies': companies
    })


# -----------------------------------------------
# Company: Post a Job
# -----------------------------------------------
@login_required
def post_job(request):
    company = CompanyProfile.objects.get(user=request.user)
    if request.method == "POST":
        Job.objects.create(
            company=company,
            title=request.POST['title'],
            package=request.POST['package'],
            details=request.POST['details'],
            min_cgpa=request.POST['min_cgpa'],
            eligible_branches=request.POST['eligible_branches']
        )
        return redirect('company_dashboard')
    return render(request, 'post_job.html')



# -----------------------------------------------
# Company: Delete a Job
# -----------------------------------------------


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if not (request.user.is_superuser or job.company.user == request.user):
        return HttpResponseForbidden("You are not allowed to delete this job.")

    if request.method == "POST":
        job.delete()
        return redirect(
            'company_dashboard' if not request.user.is_superuser else 'admin_dashboard'
        )



# -----------------------------------------------
# Student: Apply to a Job
# -----------------------------------------------
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

@login_required
def apply_job(request, job_id):
    # Ensure only students can apply
    if not hasattr(request.user, 'studentprofile'):
        return render(request, 'error.html', {
            'message': 'Only students can apply for jobs.'
        })

    student = StudentProfile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=job_id)

    # 🚫 NEW CHECK: Placement Eligibility
    if student.placement_status != "Eligible":
        return render(request, 'error.html', {
            'message': 'You are not eligible to apply for jobs.'
        })

    if request.method == "POST":

        # Check if already selected
        if Application.objects.filter(student=student, status='Selected').exists():
            return render(request, 'error.html', {
                'message': 'You are already selected and cannot apply for more jobs.'
            })

        # Check active applications (Applied or Shortlisted)
        active_apps = Application.objects.filter(
            student=student,
            status__in=['Applied', 'Shortlisted']
        ).count()

        if active_apps >= 2:
            return render(request, 'error.html', {
                'message': 'You already have 2 active applications.'
            })

        # Prevent duplicate application
        if Application.objects.filter(student=student, job=job).exists():
            return render(request, 'error.html', {
                'message': 'You have already applied for this job.'
            })

        # Create application
        Application.objects.create(
            student=student,
            job=job,
            status='Applied',
            applied_date=timezone.now()
        )

        return render(request, 'success.html', {'job': job})

    return render(request, 'apply_job.html', {'job': job})





# -----------------------------------------------
# Student: Upload Resume File
# -----------------------------------------------
@login_required
def upload_resume(request):
    student = StudentProfile.objects.get(user=request.user)
    if request.method == "POST" and request.FILES.get('resume'):
        student.resume = request.FILES['resume']
        student.save()
        return redirect('student_dashboard')
    return render(request, 'upload_resume.html')



# -----------------------------------------------
# Student: Delete Resume File
# -----------------------------------------------

@login_required
def delete_resume(request):
    student = StudentProfile.objects.get(user=request.user)

    if student.resume:
        student.resume.delete()  # deletes from MEDIA folder
        student.resume = None
        student.save()

    return redirect('student_dashboard')




# -----------------------------------------------
# Admin: Training Resources
# -----------------------------------------------

# Upload resources

@login_required
def upload_resource(request):
    if request.method == "POST":
        title = request.POST['title']
        file_link = request.FILES['file_link']
        Resource.objects.create(title=title, file_link=file_link)
        return redirect('admin_dashboard')
    return render(request, 'upload_resource.html')


# Resource view list

@login_required
def resource_list(request):
    resources = Resource.objects.all()

    return render(request, 'resource_list.html', {
        'resources': resources
    })


# Delete resource

@login_required
def delete_resource(request, resource_id):
    if not request.user.is_staff:
        return render(request, 'error.html', {'message': 'Unauthorized access'})

    resource = get_object_or_404(Resource, id=resource_id)
    resource.delete()
    return redirect('resource_list')


# view resource in student_dashboard

@login_required
def student_resources(request):
    resources = Resource.objects.all().order_by('-uploaded_at')
    return render(request, 'student_resources.html', {"resources": resources})






@login_required
def view_applicants(request, job_id):
    job = Job.objects.get(id=job_id)
    applications = Application.objects.filter(job=job)
    return render(request, 'view_applicants.html', {'job': job, 'applications': applications})





# -----------------------------------------------
# Application status : company side
# -----------------------------------------------

@login_required
def update_status(request, application_id):
    app = get_object_or_404(Application, id=application_id)

    # Safety check: Only company who posted the job should update
    if request.user != app.job.company.user:
        return render(request, 'error.html', {'message': 'Unauthorized action'})

    if request.method == "POST":
        new_status = request.POST.get('status')
        # Prevent duplicate application rows accidentally created
        # Always keep only ONE application per (student, job)
        Application.objects.filter(student=app.student, job=app.job).exclude(id=app.id).delete()
        # Save updated status
        app.status = new_status
        app.save()

    return redirect('view_applicants', job_id=app.job.id)



# -----------------------------------------------
# Application status : student side
# -----------------------------------------------


@login_required
def student_dashboard(request):
    student = StudentProfile.objects.get(user=request.user)
    jobs = Job.objects.all()

    # Get all applications by this student
    apps = Application.objects.filter(student=student)

    # Map job → application status
    job_status = {app.job.id: app.status for app in apps}

    # Attach to each job
    for job in jobs:
        job.application_status = job_status.get(job.id, None)

    context = {
        'student_profile': student,
        'jobs': jobs,
    }
    return render(request, 'student_dashboard.html', context)




# -----------------------------------------------
# Admin : View student details
# -----------------------------------------------



@login_required
def view_students(request):
    students = StudentProfile.objects.all()

    # Prepare student-wise applications
    student_data = []
    for student in students:
        applications = Application.objects.filter(student=student)
        student_data.append({
            'student': student,
            'applications': applications
        })

    return render(request, 'view_students.html', {
        'student_data': student_data
    })




# -----------------------------------------------
# Admin : View company details
# -----------------------------------------------



from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)

@login_required
@staff_required
def view_companies(request):
    # assuming your model is named CompanyProfile and has fields company_name, domain, user etc.
    companies = CompanyProfile.objects.select_related('user').all().order_by('company_name')
    return render(request, 'view_companies.html', {'companies': companies})




# -----------------------------------------------
# Logout 
# -----------------------------------------------


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
