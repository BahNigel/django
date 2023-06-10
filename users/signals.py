from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile,GoogleCalendar


@receiver(post_save, sender=User)
def create_google_calendar(sender, instance, created, **kwargs):
    if created:
        # Create a new GoogleCalendar object for the user
        calendar = GoogleCalendar(user=instance)
        # Set the credentials attribute of the GoogleCalendar object
        # to the user's OAuth2 credentials
        calendar.credentials = {
            'access_token': 'ACCESS_TOKEN',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'REFRESH_TOKEN',
            'scope': 'https://www.googleapis.com/auth/calendar',
            "web": {
                "client_id": "343290879929-n57ds4ouevp7ulfvp13ln8ataa9d0hem.apps.googleusercontent.com",
                "project_id": "boxwood-plating-389007",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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"
            }
        }
        # Set the calendar_id attribute of the GoogleCalendar object
        # to the user's primary calendar ID
        calendar.calendar_id = 'PRIMARY_CALENDAR_ID'
        # Save the GoogleCalendar object to the database
        calendar.save()