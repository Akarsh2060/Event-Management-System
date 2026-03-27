import requests
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

GMAIL_PLACEHOLDERS = {
    "your-email@gmail.com",
    "your-app-password",
    "",
}

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
    host_user = (settings.EMAIL_HOST_USER or "").strip()
    host_password = (settings.EMAIL_HOST_PASSWORD or "").strip()

    if host_user in GMAIL_PLACEHOLDERS or host_password in GMAIL_PLACEHOLDERS:
        raise ImproperlyConfigured(
            "Gmail SMTP is not configured. Update EMAIL_HOST_USER and "
            "EMAIL_HOST_PASSWORD in .env with a real Gmail address and app password."
        )

    subject = "Your OTP Verification Code"
    message = (
        f"Your OTP is: {otp}. "
        f"It is valid for {settings.OTP_EXPIRY_MINUTES} minutes."
    )
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    try:
        send_mail(
            subject,
            message,
            email_from,
            recipient_list,
            fail_silently=False,
        )
    except Exception as exc:
        logger.exception(
            "Gmail OTP send failed for %s using host=%s port=%s user=%s",
            email,
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            host_user,
        )
        raise RuntimeError(
            "Unable to send OTP email through Gmail. Check the Gmail address, "
            "app password, and SMTP access."
        ) from exc
