from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    type = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='images')

    def __str__(self):
        return self.user.username

class Blog(models.Model):
    title = models.CharField(max_length=100)
    blog_image = models.ImageField(upload_to='blog/images')
    category = models.CharField(max_length=100)
    summary = models.TextField()
    content = models.TextField()
    status = models.CharField(max_length=50)
    user_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title



class Event(models.Model):
    required_speciality = models.CharField(max_length=100)
    doctor_id = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=100)
    start_time_of_apointment = models.TimeField()
    date_of_appointment = models.DateField()

    def __str__(self):
        return self.required_speciality


class GoogleCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credentials = models.JSONField()