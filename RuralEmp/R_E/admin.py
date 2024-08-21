from django.contrib import admin
from .models import Signup, Job, WorkerHead, Feedback, Contact


@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'phoneNumber', 'userType')


# Register other models directly
admin.site.register(Job)
admin.site.register(WorkerHead)
admin.site.register(Feedback)
admin.site.register(Contact)
