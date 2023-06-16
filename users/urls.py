from django.urls import path
from . import views
from .views import CreateEventView
from .views import home_view, create_event_view, authenticate_view, callback_view

urlpatterns = [
    path('register', views.register),
    path('login', views.signin),
    path('home', views.home, name = 'dashboad'),
    path('logout', views.signout),
    path('blog/create', views.createBlog, name = 'create'),
    path('blog/', views.list, name='blog'),
    path('create-event/', CreateEventView.as_view(), name='create_event'),
    path('appointment/', views.appointment, name='appointment'),
    path('appointment-details/', views.appointmentDetails, name='success'),
    path('', home_view, name='home'),
    path('create_event/', create_event_view, name='create_event'),
    path('authenticate/', authenticate_view, name='authenticate'),
    path('authenticate/callback/', callback_view, name='callback'),
]