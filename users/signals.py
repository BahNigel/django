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
        calendar.credentials = {"web":{
                                    "client_id":"343290879929-totp9hc0o3sn202q4ju7kejksqg9cji9.apps.googleusercontent.com",
                                    "project_id":"boxwood-plating-389007","auth_uri":"https://accounts.google.com/o/oauth2/auth",
                                    "token_uri":"https://oauth2.googleapis.com/token",
                                    "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
                                    "client_secret":"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",
                                    "redirect_uris":["http://localhost:7000/authenticate"]
                                    }
                                }
        # Set the calendar_id attribute of the GoogleCalendar object
        # to the user's primary calendar ID
        calendar.calendar_id = 'PRIMARY_CALENDAR_ID'
        # Save the GoogleCalendar object to the database
        calendar.save()