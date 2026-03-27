import requests
from django.core.mail import send_mail
from django.conf import settings

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": "kd0EVmFN5KfsRiQuSUMplCG6ZHcAT4xPOeDIYJt1XrW8a2gonvD6iHkzgyFXONhK4fuv9IGMYV8lA17a",
        "Content-Type": "application/json"
    }

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def send_otp_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your OTP is: {otp}. It is valid for 5 minutes."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)