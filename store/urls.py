from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index,name = 'home'), 
    path("login/",views.loginacc,name='login'),
    path("signup/",views.signup,name='signup'),
    path("logout/",views.sign_out,name='logout'),
    path("otp_verify/",views.otp_verify,name='otp_verify'),
    path("otp/",views.otp,name='otp'),
    path("forgot_password/",views.forgot_password,name='forgot_password'),
    path('check_password/<str:uidb64>/<str:token>/', views.check_password, name='check_password'),
    path("contact/",views.contact,name='contact'),
    path("blog/",views.blog,name='blog'),
    path("reset_password/",views.reset_password,name='reset_password'),


]