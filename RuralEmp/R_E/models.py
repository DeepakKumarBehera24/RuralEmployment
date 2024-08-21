from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=30, null=False)
    numberOfWorker = models.IntegerField(null=False)
    salaryPerDay = models.IntegerField(null=False)
    machineAvailable = models.CharField(max_length=300, null=False)
    date = models.DateField(null=False)
    phoneNumber = models.BigIntegerField(null=False, default=1234567890)

    def __str__(self):
        return f"{self.name}{self.phoneNumber}"


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
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

