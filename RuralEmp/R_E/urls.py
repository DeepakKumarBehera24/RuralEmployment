from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),
    path('job/', views.job, name='job'),
    path('worker/', views.workerhead_list, name='worker'),
    path('jobform/', views.jobform, name='jobform'),
    path('workform/', views.workerhead_form, name='workform'),
    path('feedback/', views.feedback, name='feedback'),
    path('contact/', views.contact, name='contact'),
]
