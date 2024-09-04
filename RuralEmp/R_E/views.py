from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate, login
from .models import Signup, Job, WorkerHead
from django.http import HttpResponse
from django.template import loader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from itertools import combinations
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
    search_query = request.GET.get('search', '').strip()
    filter_by = request.GET.get('filter_by', '')

    myjob = Job.objects.all()
    current_time = datetime.now()

    # Determine the status of each job
    for job in myjob:
        job_end_time = datetime.combine(job.date, job.timeSpan)
        if current_time > job_end_time:
            job.status = 'done'
        else:
            job.status = 'available'

    # Apply filters based on the user's search input
    if filter_by == 'name':
        myjob = myjob.filter(name__icontains=search_query)
    elif filter_by == 'place':
        myjob = myjob.filter(place__icontains=search_query)
    elif filter_by == 'price_range_1':
        myjob = myjob.filter(price__gte=0, price__lte=5000)
    elif filter_by == 'price_range_2':
        myjob = myjob.filter(price__gt=5000, price__lte=20000)
    elif filter_by == 'price_range_3':
        myjob = myjob.filter(price__gt=20000, price__lte=50000)
    elif filter_by == 'price_range_4':
        myjob = myjob.filter(price__gt=50000)
    elif filter_by == 'date':
        try:
            search_date = datetime.strptime(search_query, '%Y-%m-%d').date()
            myjob = myjob.filter(date__iexact=search_date)
        except ValueError:
            myjob = Job.objects.none()
    elif filter_by == 'timeSpan':
        try:
            search_time = datetime.strptime(search_query, '%H:%M').time()
            myjob = myjob.filter(timeSpan__iexact=search_time)
        except ValueError:
            myjob = Job.objects.none()
    elif filter_by == 'phoneNumber':
        if search_query.isdigit():
            myjob = myjob.filter(phoneNumber__exact=int(search_query))
        else:
            myjob = Job.objects.none()

    template = loader.get_template('jobs.html')
    context = {
        'myjob': myjob,
        'search_query': search_query,
        'filter_by': filter_by,
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
    search_query = request.GET.get('search', '').strip()
    filter_by = request.GET.get('filter_by', '')

    workerheads = WorkerHead.objects.all()

    if search_query:
        if filter_by == 'name':
            workerheads = workerheads.filter(name__icontains=search_query)
        elif filter_by == 'machine':
            workerheads = workerheads.filter(machineAvailable__icontains=search_query)
        elif filter_by == 'number_of_workers':
            if search_query.isdigit():
                requested_workers = int(search_query)
                workerheads = workerheads.filter(numberOfWorker__lte=requested_workers)

                if not workerheads.exists():
                    # Try to find combinations of WorkerHead records that sum up to less than or equal to the
                    # requested number of workers
                    possible_combinations = []
                    workerheads_list = list(WorkerHead.objects.all())

                    # Check all combinations of workerheads
                    for r in range(1, len(workerheads_list) + 1):
                        for combo in combinations(workerheads_list, r):
                            if sum(w.numberOfWorker for w in combo) <= requested_workers:
                                possible_combinations.extend(combo)
                                break
                        if possible_combinations:
                            break

                    if possible_combinations:
                        workerheads = possible_combinations
                    else:
                        workerheads = WorkerHead.objects.none()  # No valid combination found
            else:
                workerheads = WorkerHead.objects.none()  # Invalid input, return no results
        elif filter_by == 'salary':
            if search_query.isdigit():
                workerheads = workerheads.filter(salaryPerDay__lte=int(search_query))
            else:
                workerheads = WorkerHead.objects.none()

    template = loader.get_template('worker.html')
    context = {
        'workerheads': workerheads,
        'search_query': search_query,
        'filter_by': filter_by,
    }
    return HttpResponse(template.render(context, request))


@login_required
def workerhead_form(request, workerhead_id=None):
    if workerhead_id:
        workerhead = get_object_or_404(WorkerHead, pk=workerhead_id, user=request.user)
    else:
        workerhead = None

    if request.method == 'POST':
        form = WorkerHeadForm(request.POST, request.FILES, instance=workerhead)
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


def machine_list(request):
    # Get filter parameters from GET request
    machine_name = request.GET.get('machine_name', '').strip()
    charge_min = request.GET.get('charge_min', '').strip()
    charge_max = request.GET.get('charge_max', '').strip()
    owner_name = request.GET.get('owner_name', '').strip()

    # Start with all machines
    machines = WorkerHead.objects.all()

    # Apply filters based on user input
    if machine_name:
        machines = machines.filter(machineAvailable__icontains=machine_name)
    if owner_name:
        machines = machines.filter(name__icontains=owner_name)
    if charge_min.isdigit():
        if charge_max.isdigit():
            machines = machines.filter(chargePerDay__gte=int(charge_min), chargePerDay__lte=int(charge_max))
        else:
            machines = machines.filter(chargePerDay__gte=int(charge_min))
    elif charge_max.isdigit():
        machines = machines.filter(chargePerDay__lte=int(charge_max))

    context = {
        'machines': machines
    }
    return render(request, 'machine_details.html', context)



@login_required
def machine_details(request, machine_id):
    try:
        machine = WorkerHead.objects.get(id=machine_id)
    except WorkerHead.DoesNotExist:
        return HttpResponse("Machine not found", status=404)

    if request.method == 'POST':
        user_name = request.POST.get('user_name', 'Anonymous')
        user_mobile = request.POST.get('user_mobile', 'N/A')

        try:
            # Email configuration
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_user = 'deepakjgrt99@gmail.com'  # Replace with your email address
            smtp_password = 'xzwyqnyirctezpti'  # Replace with your app password

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = machine.email
            msg['Subject'] = 'Interest in Your Machine'

            # Email body with user's information
            body = f'''
            A user has shown interest in your machine.

            User's Name: {user_name}
            User's Mobile Number: {user_mobile}
            '''
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(smtp_user, smtp_password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())

            return redirect('success_page')
        except smtplib.SMTPAuthenticationError as e:
            return HttpResponse(f"SMTP Authentication Error: {e}", status=500)
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    return render(request, 'machine_list.html')


def success_page(request):
    return render(request, 'success.html')

