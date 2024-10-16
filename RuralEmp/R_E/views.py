from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate, login
from .models import Signup, Job, WorkerHead, Subscription
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_POST
import smtplib
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import razorpay
from razorpay.errors import SignatureVerificationError
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
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
from django.contrib.auth import get_user_model
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)
User = get_user_model()  # This will get the User model


def signup(request):
    if request.method == 'POST':
        form = MySignupForm(request.POST)
        if form.is_valid():
            # Save the user instance
            user = form.save()  # This saves and returns a User instance

            # Ensure that 'user' is a User instance before calling handle_trial
            if isinstance(user, User):
                handle_trial(user)  # Pass the saved user instance to handle_trial
            else:
                print("Error: user is not a valid User instance")  # Debugging line

            return redirect('/login')  # After successful signup, redirect to login
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


def logout(request):
    # Clear the session
    request.session.flush()
    return redirect('/login')


def about(request):
    return render(request, 'about.html')


def job(request):
    search_query = request.GET.get('search', '').strip()
    filter_by = request.GET.get('filter_by', '')

    # Only display jobs that are not marked as done and haven't expired
    myjob = Job.objects.filter(work_done=False)
    current_time = timezone.now()

    # Determine the status of each job
    for job in myjob:
        job_end_time = job.date + timedelta(days=job.days)  # Calculate end date
        if current_time.date() > job_end_time:
            job.status = 'done'
        else:
            job.status = 'available'

    # Apply filters based on the user's search input
    if filter_by == 'name':
        myjob = myjob.filter(name__icontains=search_query)
    elif filter_by == 'place':
        myjob = myjob.filter(place__icontains=search_query)
    # Additional filters can be added here

    template = loader.get_template('jobs.html')
    context = {
        'myjob': myjob,
        'search_query': search_query,
        'filter_by': filter_by,
    }
    return HttpResponse(template.render(context, request))


@login_required
def mark_done(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user == job.user:
        job.work_done = True
        job.save()
    return redirect('job')  # Redirect to the jobs list after marking done# Redirect to the job listing page


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
            users = User.objects.all()  # Fetch all users to pass to the template
            return render(request, 'jobform.html', {'form': form, 'error': 'There was an error with your submission.', 'users': users})
    else:
        form = MyJobs(instance=job)
        users = User.objects.all()  # Fetch all users to pass to the template
    return render(request, 'jobform.html', {'form': form, 'users': users})


@login_required
def workerhead_list(request):
    search_query = request.GET.get('search', '').strip()
    filter_by = request.GET.get('filter_by', '')

    workerheads = WorkerHead.objects.all()

    if filter_by.startswith('salary_range_'):
        if filter_by == 'salary_range_1':
            workerheads = workerheads.filter(salaryPerDay__range=(0, 5000))
        elif filter_by == 'salary_range_2':
            workerheads = workerheads.filter(salaryPerDay__range=(5000, 20000))
        elif filter_by == 'salary_range_3':
            workerheads = workerheads.filter(salaryPerDay__range=(20000, 50000))
        elif filter_by == 'salary_range_4':
            workerheads = workerheads.filter(salaryPerDay__gt=50000)

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
        elif filter_by == 'name':
            workerheads = workerheads.filter(name__icontains=search_query)
        elif filter_by == 'machine':
            workerheads = workerheads.filter(machineAvailable__icontains=search_query)

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


@login_required
def machine_list(request):
    # Get filter parameters from GET request
    machine_name = request.GET.get('machine_name', '').strip()
    charge_min = request.GET.get('charge_min', '').strip()
    charge_max = request.GET.get('charge_max', '').strip()
    owner_name = request.GET.get('owner_name', '').strip()

    # Start with all machines
    machines = WorkerHead.objects.all()

    # Filter based on booking status
    if not request.user.is_authenticated:
        machines = machines.filter(is_booked=False)
    else:
        # Allow authenticated users to see their own booked machines
        machines = machines.filter(Q(is_booked=False) | Q(user=request.user))

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
    return render(request, 'machine_list.html', context)


@login_required
def machine_details(request, machine_id):
    machine = get_object_or_404(WorkerHead, id=machine_id)

    if request.method == 'POST':
        if 'toggle_booking' in request.POST:
            if request.user == machine.user:
                machine.is_booked = not machine.is_booked
                machine.save()
                return redirect('machine_list')

        # Admin can cancel the booking (this part will only appear after booking)
        if 'cancel_booking' in request.POST:
            if request.user == machine.user and machine.is_booked:
                machine.is_booked = False
                machine.save()
                return redirect('machine_list')

        if 'user_name' in request.POST and 'user_mobile' in request.POST:
            user_name = request.POST.get('user_name', 'Anonymous')
            user_mobile = request.POST.get('user_mobile', 'N/A')

            try:
                # SMTP Email configuration
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_user = 'deepakjgrt99@gmail.com'  # Replace with your email
                smtp_password = 'xzwyqnyirctezpti'  # Replace with your app password

                # Create the email message
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = machine.email
                msg['Subject'] = 'Interest in Your Machine'

                body = f'''
                A user has shown interest in your machine.

                User's Name: {user_name}
                User's Mobile Number: {user_mobile}
                '''
                msg.attach(MIMEText(body, 'plain'))

                # Connect to the SMTP server and send the email
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()  # Secure the connection
                    server.login(smtp_user, smtp_password)
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                return redirect('success_page')
                # Redirect to success page or back to the machine details page
                # return redirect('machine_details', machine_id=machine_id)

            except smtplib.SMTPAuthenticationError as e:
                return HttpResponse(f"SMTP Authentication Error: {e}", status=500)

            except Exception as e:
                return HttpResponse(f"An error occurred: {e}", status=500)

    return render(request, 'machine_details.html', {'machine': machine})


def success_page(request):
    return render(request, 'success.html')


@login_required
def toggle_booking(request, worker_head_id):
    try:
        machine = WorkerHead.objects.get(id=worker_head_id)
    except WorkerHead.DoesNotExist:
        return HttpResponse("Machine not found", status=404)

    # Toggle booking status
    machine.is_booked = not machine.is_booked
    machine.save()

    return redirect('machine_list')  # Redirect to the list or detail page


SUBSCRIPTION_DURATIONS = {
    '1_month': 30,
    '6_months': 180,
    '1_year': 365,
}
SUBSCRIPTION_PRICES = {
    '1_month': 199,
    '6_months': 899,
    '1_year': 1199,
    'lifetime': 5999,
}


# Function to subscribe user
def subscribe_user(user, subscription_type):
    if subscription_type in SUBSCRIPTION_DURATIONS:
        duration = SUBSCRIPTION_DURATIONS[subscription_type]
    else:
        duration = None  # Lifetime subscription

    subscription, created = Subscription.objects.get_or_create(user=user)
    if subscription_type == 'lifetime':
        subscription.set_subscription(None)  # Lifetime access
    else:
        subscription.set_subscription(duration)
    subscription.subscription_type = subscription_type
    subscription.save()


# Subscription page view
@login_required
def subscription_page(request):
    subscription = Subscription.objects.get(user=request.user)

    # Handle subscription form submission
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        if subscription_type:
            subscribe_user(request.user, subscription_type)
            return redirect('payment')  # Redirect to payment after subscription
        else:
            messages.error(request, 'Please choose a subscription plan.')

    return render(request, 'subscription.html', {'user': request.user})


# Handling free trial
def handle_trial(user):
    subscription, created = Subscription.objects.get_or_create(user=user)
    if not subscription.is_trial:
        subscription.set_trial()
        subscription.save()
        return True
    return False


# Payment initiation
def initiate_payment(user, subscription_type):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    price = SUBSCRIPTION_PRICES[subscription_type] * 100  # Convert rupees to paise

    # Create Razorpay order
    payment = client.order.create({
        'amount': price,
        'currency': 'INR',
        'payment_capture': '1',
        'receipt': f"{user.id}_{subscription_type}",
    })

    # Return payment details needed for the frontend
    return {
        'key_id': settings.RAZORPAY_KEY_ID,  # Razorpay key ID
        'amount': payment['amount'],  # Payment amount in paisa
        'order_id': payment['id'],  # Razorpay Order ID
    }


@login_required
def payment_view(request):
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        if subscription_type and subscription_type in SUBSCRIPTION_PRICES:
            payment = initiate_payment(request.user, subscription_type)
            return render(request, 'payment.html', {'payment': payment})
        else:
            return redirect('subscription_page')
    return redirect('subscription_page')


def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            if subscription.is_active():
                return view_func(request, *args, **kwargs)
            return redirect('subscription_page')
        return redirect('/login')
    return wrapper


# Initialize Razorpay client with your key and secret from Django settings
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
@csrf_exempt  # Since it's a JSON request
def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        # Verify the payment using Razorpay's signature verification
        try:
            # Prepare the signature verification data
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # This method verifies the signature and raises an exception if invalid
            razorpay_client.utility.verify_payment_signature(params_dict)

            # If verification passes, update the subscription
            subscription = Subscription.objects.get(user=request.user)
            subscription.is_active = True
            subscription.save()

            return JsonResponse({'success': True})

        except SignatureVerificationError:
            # Handle signature verification failure
            return JsonResponse({'success': False, 'error': 'Signature verification failed'})

    # Return an error if the method is not POST
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# @subscription_required
def home(request):
    # user = request.user
    # subscription, created = Subscription.objects.get_or_create(user=user)
    # if subscription.is_active():
    #     feedbacks = Feedback.objects.all()  # Query all feedbacks
    #     context = {
    #         'feedbacks': feedbacks,
    #         'range': range(1, 6),  # This creates a range from 1 to 5
    #         'subscription': subscription,  # Add subscription to context
    #     }
    #     return render(request, 'home.html', context)
    # else:
    #     return redirect('subscription_page')
    feedbacks = Feedback.objects.all()  # Assuming you're querying all feedbacks
    context = {
        'feedbacks': feedbacks,
        'range': range(1, 6)  # This creates a range from 1 to 5
    }
    return render(request, 'home.html', context)


# openai.api_key = 'sk-proj-oQKbl6LhOKOch4ey1PHzAK9SWGwtivFlrgATW_iwabYji3jYH49aBp1oWYwjlx2
# -s4z3o5upFST3BlbkFJ6zyS1u3vjxFy24QWdmuyVWGoJ9WcijuDArtkPUB9LObxdMsTADqVBgf8kS_iJgRaMu9IBVnLEA'

# Initialize tokenizer and model globally
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message').strip().lower()

        # Dictionary of predefined responses
        responses = {
            'job postings': 'We have various job postings available. You can view them on the Jobs page.',
            'worker details': 'You can find worker details on the Worker Head page.',
            'machine details': 'Machine details can be found on the Machine List page.',
            'feedback': 'You can provide feedback on the Feedback page.',
            'subscription': 'For subscription details, please visit the Subscription page.',
            'contact support': 'For support, please contact us at 9777256310',
            'how to post a job': 'To post a job, go to the Jobs page and click on "Post Job".',
            'how to hire a worker': 'To hire a worker, visit the Worker Head page and select a worker.',
            'how to rent a machine': 'Machine rental details are available on the Machine List page.',
            'subscription plans': 'We offer several subscription plans. Check the Subscription page for more details.',
            'website features': 'Our website offers job postings, worker details, machine rentals, and feedback '
                                'options.',
            'pricing': 'Job postings are free, but you may need a subscription for advanced features.',
            'how to leave feedback': 'You can leave feedback on the Feedback page.',
            'about us': 'Gram Setu is dedicated to connecting farmers with workers and machinery.',
            'user registration': 'You can register on the SignUp page. After registration, you can log in to use all '
                                 'features.',
            'forgot password': 'If you forgot your password, use the "Forgot Password" link on the login page.',
            'how to update profile': 'Update your profile details by visiting your account settings page.',
            'how to delete account': 'To delete your account, please contact support at deepakjgrt99@gmail.com',
            'privacy policy': 'Read our privacy policy on the Privacy Policy page.',
            'terms and conditions': 'Our terms and conditions can be found on the Terms page.',
            'how to contact us': 'Contact us via email at deepakjgrt99@gmail.com or through our contact form.',
            'how to use the website': 'Explore different pages to learn about job postings, worker details, and more.',
            'technical issues': 'For technical issues, please reach out to our support team at deepakjgrt99@gmail.com.',
            'new features': 'Stay tuned to our website for updates on new features and improvements.',
        }

        # Return the corresponding response, or a default message if the input doesn't match any key
        response_message = responses.get(user_message, "Sorry, I didn't understand that. Can you try rephrasing?")

        return JsonResponse({'response': response_message})

    # For non-POST requests, return an error
    return JsonResponse({'error': 'Invalid request method'}, status=405)
