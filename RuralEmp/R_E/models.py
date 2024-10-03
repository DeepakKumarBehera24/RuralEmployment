from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class Signup(models.Model):
    USER_TYPE = [
        ('worker head', 'Worker Head'),
        ('job provider', 'Job Provider')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='signup', default=1)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    DOB = models.DateField()
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=15)
    phoneNumber = models.CharField(max_length=15, unique=True)
    userType = models.CharField(max_length=20, choices=USER_TYPE, default='worker head')
    adharNumber = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


class WorkerHead(models.Model):
    id = models.AutoField(primary_key=True)  # Django adds this automatically
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=30, null=False)
    numberOfWorker = models.IntegerField(null=False)
    salaryPerDay = models.IntegerField(null=False)
    machineAvailable = models.CharField(max_length=300, null=False)
    machineImage = models.ImageField(upload_to='machines/', null=True, blank=True)
    chargePerDay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateField(null=False)
    phoneNumber = models.BigIntegerField(null=False, default=1234567890)
    email = models.EmailField(max_length=254, null=True, blank=True)  # New email field
    is_booked = models.BooleanField(default=False)  # New field to track booking status

    def __str__(self):
        return f"{self.name} - {self.phoneNumber}"


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=30, null=False)
    jobDescription = models.TextField(null=True)
    place = models.CharField(max_length=50)
    price = models.IntegerField(null=False)
    date = models.DateField(null=False, default='2024-08-20')
    days = models.IntegerField(null=False, default=0)
    timeSpan = models.TimeField(null=False)
    phoneNumber = models.BigIntegerField(null=False, default=None)

    def __str__(self):
        return f"{self.name}"


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)  # Rating from 1 to 5
    # (1 is the lowest and 5 is the highest rating here)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} on {self.date}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} on {self.date}"


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_trial = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    subscription_type = models.CharField(max_length=20, choices=[
        ('7_days', '7-Day Trial'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('lifetime', 'Lifetime')
    ])

    def is_active(self):
        if self.subscription_type == 'lifetime':
            return True
        return self.end_date and timezone.now() <= self.end_date

    def set_trial(self):
        self.start_date = timezone.now()
        self.end_date = timezone.now() + timedelta(days=7)
        self.is_trial = True

    def set_subscription(self, duration_days):
        self.start_date = timezone.now()
        self.end_date = timezone.now() + timedelta(days=duration_days)
        self.is_trial = False





