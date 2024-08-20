from django import forms
from .models import *


class MySignup(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    reEnter = forms.CharField(widget=forms.PasswordInput, label="Re-enter Password")
    DOB = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d']  # Accepts both 'DD-MM-YYYY' and 'YYYY-MM-DD'
    )

    class Meta:
        model = Signup
        fields = ['firstName', 'lastName', 'DOB', 'city', 'state', 'phoneNumber', 'userType', 'adharNumber', 'password']

        widgets = {
            'userType': forms.RadioSelect(choices=Signup.USER_TYPE),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        reEnter = cleaned_data.get("reEnter")

        if password and reEnter and password != reEnter:
            raise forms.ValidationError("Passwords do not match. Please enter them again.")

        return cleaned_data


class MyLogin(forms.Form):
    phoneNumber = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)


class WorkerHeadForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d']
    )

    class Meta:
        model = WorkerHead
        fields = '__all__'


class MyJobs(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d']
    )

    class Meta:
        model = Job
        fields = '__all__'


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'feedback', 'rating']
        widgets = {
            'rating': forms.Select(choices=Feedback._meta.get_field('rating').choices),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

