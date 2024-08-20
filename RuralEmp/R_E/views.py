from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import Signup, Job, WorkerHead
from django.http import HttpResponse
from django.template import loader
from .forms import MySignup, MyLogin, WorkerHeadForm, MyJobs, Feedback, FeedbackForm, ContactForm


def signup(request):
    if request.method == 'POST':
        signupForm = MySignup(request.POST)
        if signupForm.is_valid():
            phoneNumber = signupForm.cleaned_data['phoneNumber']
            password = signupForm.cleaned_data['password']

            # Check if user with the provided phone number already exists
            if Signup.objects.filter(phoneNumber=phoneNumber).exists():
                # Redirect to login if user already exists
                return redirect('/login')

            # Create and save a new user
            user = signupForm.save(commit=False)
            user.password = make_password(password)  # Hash the password before saving
            user.save()
            return redirect('/login')
        else:
            print(signupForm.errors)  # Debug: Print form errors if validation fails
    else:
        signupForm = MySignup()

    return render(request, 'signUp.html', {'form': signupForm})


def login(request):
    if request.method == 'POST':
        form = MyLogin(request.POST)
        if form.is_valid():
            phoneNumber = form.cleaned_data['phoneNumber']
            password = form.cleaned_data['password']

            try:
                user = Signup.objects.get(phoneNumber=phoneNumber)

                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    print(f"User {user.id} logged in successfully.")
                    return redirect('home')
                else:
                    print("Invalid password.")
                    return render(request, 'login.html', {'form': form, 'error': 'Invalid phone number or password'})
            except Signup.DoesNotExist:
                print("User does not exist.")
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
    myjob = Job.objects.all().values()
    template = loader.get_template('jobs.html')
    context = {
        'myjob': myjob
    }
    return HttpResponse(template.render(context, request))


def jobform(request):
    if request.method == 'POST':
        form = MyJobs(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/job')  # Redirect to a URL after successful submission
        else:
            return render(request, 'jobform.html', {'form': form, 'error': 'There was an error with your submission.'})
    else:
        form = MyJobs()
    return render(request, 'jobform.html', {'form': form})


def workerhead_form(request):
    if request.method == 'POST':
        form = WorkerHeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/worker')  # Redirect to a URL after successful submission
        else:
            return render(request, 'workerform.html', {'form': form, 'error': 'There was an error with your submission.'})
    else:
        form = WorkerHeadForm()
    return render(request, 'workerform.html', {'form': form})


def workerhead_list(request):
    workerheads = WorkerHead.objects.all().values()
    template = loader.get_template('worker.html')
    context = {
        'workerheads': workerheads
    }
    return HttpResponse(template.render(context, request))


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
