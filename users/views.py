from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from django.shortcuts import render, redirect
from .forms import ExtendedUserCreationForm , blogForm
from django.contrib.auth import login, authenticate, logout
from . import models
import base64
from datetime import datetime, timedelta
from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import render
from django.views import View
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from .models import GoogleCalendar,Event,UserProfile, Blog


def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'users/register.html',{'form': form})

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboad')

    return render(request, 'users/login.html')

def home(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user =  models.UserProfile.objects.filter(user_id=user_id).select_related('user').first()
        return render(request, 'users/home.html',{'user':user})
    else:
        return redirect('/login')


def signout(request):
    logout(request)
    return redirect('/login')

def createBlog(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        profile = models.UserProfile.objects.filter(user_id=user_id).values().first()
        form = blogForm()
        if profile['type'] == "2":
            return redirect('dashboad')
        else:
            if request.method == 'POST':
                form = blogForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    return redirect('dashboad')
                else:
                    form = blogForm()
            return render(request, 'blog/create.html',{'form': form, 'user_id': user_id})
    else:
        return redirect('/login')



def list(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user =  models.UserProfile.objects.filter(user_id=user_id).select_related('user').first()
        users =  models.UserProfile.objects.filter(type='1').select_related('user').all()
        for use in users:
            value = use.user.id
            use.user.id = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
        posts = models.Blog.objects.all()
        tiems = models.Blog.objects.values('category').distinct()
        if request.GET.get('category'):
            category = request.GET.get('category')
            posts = models.Blog.objects.filter(category=category).all()

        return render(request, 'blog/list.html',{'user':user, 'posts':posts, 'tiems':tiems, 'users':users })


class CreateEventView(View):
    def get(self, request):
        calendar = GoogleCalendar.objects.get(user=request.user)
        credentials = Credentials.from_authorized_user_info(info=calendar.credentials)

        try:
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': 'Test Event',
                'start': {
                    'dateTime': '2022-01-01T10:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': '2022-01-01T12:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')
        except HttpError as error:
            print(f'An error occurred: {error}')
            return render(request, 'event/error.html', {'error': error})

        return render(request, 'event/success.html')

def appointment(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        if request.GET.get('d'):
            value = request.GET.get('d')
            doctor_id = int(base64.b64decode(value.encode('utf-8')).decode('utf-8'))
        else:
            return redirect('/blog')
        if request.method == 'POST':
            required_speciality = request.POST['required_speciality']
            start_time_of_apointment = request.POST['start_time_of_apointment']
            date_of_appointment = request.POST['date_of_appointment']
            event = Event(required_speciality=required_speciality, doctor_id=doctor_id,
                          patient_id=user_id, start_time_of_apointment=start_time_of_apointment,
                          date_of_appointment=date_of_appointment)
            event.save()
            return redirect('create_event')
            # return redirect('success')
        return render(request, 'event/appointment.html', {'user_id': user_id, 'doctor_id': doctor_id})
    else:
        return redirect('/login')

def appointmentDetails(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user_profile = UserProfile.objects.filter(user_id=user_id).select_related('user').first()
        users = UserProfile.objects.filter(type='1').select_related('user').all()
        appointments = Event.objects.filter(
            Q(patient_id=user_id)
        ).prefetch_related('doctor_id__user', 'doctor_id__userProfile')
        print(user_profile.type)
        for appointment in appointments:
            start_time = datetime.combine(datetime.today(), appointment.start_time_of_apointment)
            end_time = start_time + timedelta(minutes=45)
            appointment.end_time = end_time.time()

        for use in users:
            value = use.user.id
            use.user.id = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')

        posts = Blog.objects.all()
        times = Blog.objects.values('category').distinct()

        if request.GET.get('category'):
            category = request.GET.get('category')
            posts = Blog.objects.filter(category=category).all()

        return render(request, 'event/success.html',{'user':user_profile, 'posts':posts, 'times':times, 'users':users, 'appointments': appointments})