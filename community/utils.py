from twilio.rest import Client
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)

def send_event_notification(user, event):
    domain = get_current_site(None).domain
    url = f"https://{domain}{event.get_absolute_url()}"

    message = f"Event Alert: {event.title}\nWhen: {event.date}\nJoin: {url}"

    # SMS
    if user.profile.phone:
        client.messages.create(
            to=user.profile.phone,
            from_='+1234567890',
            body=message[:160]
        )

    # WhatsApp
    if user.profile.whatsapp_optin:
        client.messages.create(
            to=f"whatsapp:{user.profile.phone}",
            from_=settings.TWILIO_WHATSAPP,
            body=message
        )