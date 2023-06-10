from django.urls import path
from . import views
from .views import CreateEventView

urlpatterns = [
    path('register', views.register),
    path('login', views.signin),
    path('', views.home, name = 'dashboad'),
    path('logout', views.signout),
    path('blog/create', views.createBlog, name = 'create'),
    path('blog/', views.list, name='blog'),
    path('create-event/', CreateEventView.as_view(), name='create_event'),
    path('appointment/', views.appointment, name='appointment'),
    path('appointment-details/', views.appointmentDetails, name='success'),
]