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

from django.shortcuts import render
from django.http import HttpResponse
from users.google_calendar import get_events, create_event
from datetime import datetime, time, timedelta

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib import flow
import datetime
import pytz

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



def home(request):
    events = get_events()
    context = {'events': events}
    return render(request, 'home.html', context)

def create(request):
    if request.method == 'POST':
        summary = request.POST.get('summary')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        timezone = request.POST.get('timezone')

        if not start_time or not end_time:
            return HttpResponse('Please enter start and end times.')

        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

        create_event(summary, start_time.isoformat(), end_time.isoformat(), timezone)

        return HttpResponse('Event created successfully.')

    return render(request, 'create.html')


# Set up the Google Calendar API client
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'client_secret.json'
calendar_service = build('calendar', 'v3', credentials=Credentials.from_authorized_user_file('token.json', SCOPES))

def home_view(request):
    # Get the user's events for the next week
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    week_later = (datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).isoformat() + 'Z'
    events_result = calendar_service.events().list(calendarId='primary', timeMin=now, timeMax=week_later, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        message = 'No upcoming events found.'
    else:
        message = 'Upcoming events:'
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.datetime.fromisoformat(start).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
            message += f'\n{start_time} - {event["summary"]}'
    return render(request, 'home.html', {'message': message})

def create_event_view(request):
    if request.method == 'POST':
        # Get the event details from the form
        summary = request.POST['summary']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        # Create an event object
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        # Add the event to the user's calendar
        try:
            calendar_service.events().insert(calendarId='primary', body=event).execute()
            message = 'Event created successfully.'
        except HttpError as error:
            message = f'An error occurred: {error}'
        return render(request, 'create.html', {'message': message})
    else:
        return render(request, 'create.html')

def authenticate_view(request):
    # Set up the Google Calendar API credentials flow
    flows = flow.Flow.from_client_secrets_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    flows.redirect_uri = 'http://localhost:7000/authenticate'

    # Generate the authorization URL and redirect the user to Google sign-in
    authorization_url, state = flows.authorization_url(
        access_type='offline', include_granted_scopes='true')
    request.session['state'] = state
    return HttpResponseRedirect(authorization_url)

def callback_view(request):
    # Exchange the authorization code for access and refresh tokens
    state = request.session['state']
    flows = flow.Flow.from_client_secrets_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, state=state)
    flows.redirect_uri = 'http://localhost:7000/authenticate'
    authorization_response = request.build_absolute_uri()
    flows.fetch_token(authorization_response=authorization_response)

    # Save the access and refresh tokens to a file
    credentials = flows.credentials
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())

    # Redirect the user back to the home page
    return HttpResponseRedirect(reverse('home'))