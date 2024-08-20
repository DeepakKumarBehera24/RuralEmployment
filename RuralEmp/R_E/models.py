from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Signup(models.Model):
    USER_TYPE = [
        ('worker head', 'Worker Head'),
        ('job provider', 'Job Provider')
    ]

    firstName = models.CharField(max_length=20, null=False)
    lastName = models.CharField(max_length=20, null=False)
    DOB = models.DateField(null=False)
    city = models.CharField(max_length=30, null=False)
    state = models.CharField(max_length=15, null=False)
    phoneNumber = models.CharField(max_length=15, unique=True)  # Changed to CharField for phone numbers
    userType = models.CharField(max_length=20, choices=USER_TYPE, default='worker head')
    adharNumber = models.CharField(max_length=16)  # Changed to CharField for adharNumber
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


class WorkerHead(models.Model):
    name = models.CharField(max_length=30, null=False)
    numberOfWorker = models.IntegerField(null=False)
    salaryPerDay = models.IntegerField(null=False)
    machineAvailable = models.CharField(max_length=300, null=False)
    date = models.DateField(null=False)

    def __str__(self):
        return f"{self.name}"


class Job(models.Model):
    name = models.CharField(max_length=30, null=False)
    jobDescription = models.TextField(null=True)
    place = models.CharField(max_length=50)
    price = models.IntegerField(null=False)
    date = models.DateField(null=False, default='2024-08-20')
    timeSpan = models.TimeField(null=False)
    phoneNumber = models.BigIntegerField(null=False, default=1234567890)

    def __str__(self):
        return f"{self.name}"


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # Rating from 1 to 5
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


