from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate, login
from .models import Signup, Job, WorkerHead
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .forms import MySignupForm, MyLogin, WorkerHeadForm, MyJobs, Feedback, FeedbackForm, ContactForm


def signup(request):
    if request.method == 'POST':
        form = MySignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
        else:
            print(form.errors)  # Debug: Print form errors if validation fails
    else:
        form = MySignupForm()

    return render(request, 'signUp.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = MyLogin(request.POST)
        if form.is_valid():
            phoneNumber = form.cleaned_data['phoneNumber']
            password = form.cleaned_data['password']

            # Authenticate the user using phoneNumber as username
            user = authenticate(request, username=phoneNumber, password=password)

            if user is not None:
                auth_login(request, user)  # Log the user in using the correct function
                print(f"User {user.username} logged in successfully.")
                return redirect('home')  # Redirect to home or another URL
            else:
                print("Invalid password or username.")
                return render(request, 'login.html', {'form': form, 'error': 'Invalid phone number or password'})
    else:
        form = MyLogin()

    return render(request, 'login.html', {'form': form})


def home(request):
    feedbacks = Feedback.objects.all()  # Assuming you're querying all feedbacks
    context = {
        'feedbacks': feedbacks,
        'range': range(1, 6)  # This creates a range from 1 to 5
    }
    return render(request, 'home.html', context)


def logout(request):
    # Clear the session
    request.session.flush()
    return redirect('/login')


def about(request):
    return render(request, 'about.html')


def job(request):
    myjob = Job.objects.all()
    current_time = datetime.now()

    # Determine the status of each job
    for job in myjob:
        job_end_time = datetime.combine(job.date, job.timeSpan)
        if current_time > job_end_time:
            job.status = 'done'
        else:
            job.status = 'available'

    template = loader.get_template('jobs.html')
    context = {
        'myjob': myjob
    }
    return HttpResponse(template.render(context, request))


@login_required
def jobform(request, job_id=None):
    if job_id:
        job = get_object_or_404(Job, pk=job_id, user=request.user)
    else:
        job = None

    if request.method == 'POST':
        form = MyJobs(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            return redirect('/job')
        else:
            return render(request, 'jobform.html', {'form': form, 'error': 'There was an error with your submission.'})
    else:
        form = MyJobs(instance=job)
    return render(request, 'jobform.html', {'form': form})


@login_required
def workerhead_list(request):
    workerheads = WorkerHead.objects.all()
    template = loader.get_template('worker.html')
    context = {
        'workerheads': workerheads
    }
    return HttpResponse(template.render(context, request))


@login_required
def workerhead_form(request, workerhead_id=None):
    if workerhead_id:
        workerhead = get_object_or_404(WorkerHead, pk=workerhead_id, user=request.user)
    else:
        workerhead = None

    if request.method == 'POST':
        form = WorkerHeadForm(request.POST, instance=workerhead)
        if form.is_valid():
            workerhead = form.save(commit=False)
            workerhead.user = request.user
            workerhead.save()
            return redirect('/worker')
        else:
            return render(request, 'workerform.html',
                          {'form': form, 'error': 'There was an error with your submission.'})
    else:
        form = WorkerHeadForm(instance=workerhead)
    return render(request, 'workerform.html', {'form': form})


@login_required
def delete_worker(request, workerhead_id):
    workerhead = get_object_or_404(WorkerHead, pk=workerhead_id, user=request.user)
    if request.method == 'POST':
        workerhead.delete()
        return redirect('/worker')
    return render(request, 'confirm_delete.html', {'object': workerhead})


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact_success.html')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, user=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('/job')
    return render(request, 'confirm_delete.html', {'object': job})
