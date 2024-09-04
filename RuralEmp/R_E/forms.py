from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class MySignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Re-enter Password")
    DOB = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d']
    )
    userType = forms.ChoiceField(choices=Signup.USER_TYPE, widget=forms.RadioSelect)

    class Meta:
        model = Signup
        fields = ['firstName', 'lastName', 'DOB', 'city', 'state', 'phoneNumber', 'userType', 'adharNumber']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please enter them again.")

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['phoneNumber'],  # or another unique identifier
            password=self.cleaned_data['password1']
        )
        signup = super().save(commit=False)
        signup.user = user
        if commit:
            signup.save()
        return signup


class MyLogin(forms.Form):
    phoneNumber = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)


class WorkerHeadForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d']
    )

    email = forms.EmailField(
        required=True,  # Make the email field required
        widget=forms.EmailInput(attrs={'placeholder': 'Enter owner email'})
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

