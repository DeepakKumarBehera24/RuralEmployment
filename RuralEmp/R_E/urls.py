from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),
    path('job/', views.job, name='job'),
    path('worker/', views.workerhead_list, name='worker'),  # Ensure this name matches your template
    path('jobform/', views.jobform, name='jobform'),
    path('workform/', views.workerhead_form, name='workform'),
    path('feedback/', views.feedback, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('jobform/<int:job_id>/', views.jobform, name='edit_job'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('workerform/<int:workerhead_id>/', views.workerhead_form, name='edit_worker'),
    path('worker/<int:workerhead_id>/delete/', views.delete_worker, name='delete_worker'),
]
