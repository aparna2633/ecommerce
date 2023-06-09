from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account
from product.models import Product,Category,SubCategory,CartItems,Banner,GuestCart
from .forms import *
from django.contrib.auth.hashers import check_password
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from AdminPanel.views import adminHome
from django.views.decorators.cache import never_cache
import twilio
from twilio.rest import Client
import os
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.urls import reverse


# from twilio.rest import Client

# Create your views here.

def index(request):
    # if request.user.is_authenticated:
    products = Product.objects.all()
    banner = Banner.objects.all()
    return render(request, 'index.html',{'products':products,'banner':banner})


#user login
@cache_control(no_cache=True, must_revalidate=True)
def loginacc(request):
    if request.user.is_authenticated and not request.user.is_staff:
        print(request.user)
        return redirect(index)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                    # Log the user in 
                if user.is_staff:
                    messages.error(request, "You are not authorized to access this webpage!!!")
                    return render(request, 'user_login.html',{'form': form})
                
                if not request.session.session_key:
                    request.session.create()
                request.session['guest_key']=request.session.session_key
                sessionId = request.session['guest_key']
                login(request, user)
                guest_item = GuestCart.objects.filter(user_ref=sessionId).values()
                for i in guest_item:
                    # print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii:",i)
                    i.pop('user_ref')
                    i['user'] = request.user
                    CartItems.objects.create(**i)
                guest_item = GuestCart.objects.filter(user_ref=sessionId)
                guest_item.delete()
                print("logged!!")
               
                return redirect(index)
            else:
                messages.error(request, 'Email Id or Password is wrong!')
                return redirect(loginacc)
    else:
        form = LoginForm()
        return render(request, 'user_login.html', {'form': form})


def otp(request):
    if request.method=='POST':
        phone = request.POST['phone']
        request.session["phone"] = phone
        if Account.objects.filter(phone=phone).exists():
            print(phone)
            account_sid =   os.getenv('ACCOUNT_SID') or 'ACdafc08625ab5b23aac0feec99142c377'
            auth_token = os.getenv('AUTH_TOKEN') or '46bd02ba1fd1dd692fb8dc81afbb719a'
            service_sid = os.getenv('SERVICE_SID') or 'VA5774a25100d8a4e5e1324832da6896aa'
            print(account_sid,auth_token)
            client = Client(account_sid, auth_token)
            verification = client.verify \
                     .v2 \
                     .services(service_sid) \
                     .verifications \
                     .create(to='[+91]'+str(phone), channel='sms')
            print(verification)
            if Account.objects.filter(phone=phone).exists():
                    return redirect(otp_verify)
        else:
            messages.error(request, "You are not a registered user!")
            return redirect(loginacc)
    return render(request,'otp_login.html')

def otp_verify(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        phone = request.session.get('phone')
        print(phone)
        account_sid =   os.getenv('ACCOUNT_SID') or 'ACdafc08625ab5b23aac0feec99142c377'
        auth_token = os.getenv('AUTH_TOKEN') or '46bd02ba1fd1dd692fb8dc81afbb719a'
        service_sid = os.getenv('SERVICE_SID') or 'VA5774a25100d8a4e5e1324832da6896aa'
        client = Client(account_sid, auth_token)
        try:
            verification_check = client.verify \
                           .v2 \
                           .services(service_sid) \
                           .verification_checks \
                           .create(to='[+91]'+str(phone), code=otp)
            if verification_check.status == 'approved':
                user = Account.objects.get(phone=phone)
                login(request,user)
                return redirect(index)
            else:
                messages.error(request, ("Wrong OTP"))
        except twilio.TwilioException as e:
            messages.error(request, ("Wrong OTP"))
    return render(request, 'otp.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if not name.isalpha():
                messages.error(request, "Name should contain only characters!")
            elif len(name) < 2:
                messages.error(request, "Name should be at least 2 characters long!")
            elif password != confirm_password:
                messages.error(request, "Passwords do not match!")
            else:
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, "Please enter a valid email address!")
                else:
                    try:
                        Account.objects.get(email=email)
                        messages.error(request, "User with this email already exists!")
                    except ObjectDoesNotExist:
                        pass
                    if not phone.isdigit() or len(phone) != 10:
                        messages.error(request, "Please enter a valid 10-digit phone number!")
                    else:
                        try:
                            Account.objects.get(phone=phone)
                            messages.error(request, "User with this phone number already exists!")
                        except ObjectDoesNotExist:
                            pass
                        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                            messages.error(request, "Password should be at least 8 characters long and should contain at least one letter and one number!")
                        else:
                            user = Account.objects.create_user(name, email, phone, password)
                            user.name = name
                            user.email = email
                            user.phone = phone
                            user.save()
                            messages.success(request, "Registered Successfully!")
                            return redirect(loginacc)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        print("LoggedOut")
        # messages.success(request, 'Logged Out Successfully')
        return redirect(index)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        request.session['email'] = email
        users = Account.objects.filter(email=email)
        for user in users:
            if user.email == email:
                return render(request, 'password_reset.html')
            else:
                messages.error(request,'you are not registered')
    return render(request, "forgot_password.html")

def reset_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        email = request.session.get('email')
        user = Account.objects.get(email=email)
        print(user)
        new_password = make_password(password)
        print(new_password)
        user.password = new_password
        if password != password1:
            messages.error(request, "Passwords do not match!")
            return render(request,'password_reset.html')
        user.save()
    messages.success(request,'Password has been changed')
    return redirect(loginacc)

def contact(request):
    return render(request,'contact.html')

def blog(request):
    return render(request,'blog.html')