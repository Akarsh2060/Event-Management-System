import requests
import logging
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

GMAIL_PLACEHOLDERS = {
    "your-email@gmail.com",
    "your-app-password",
    "",
}


def _mask_secret(value):
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"

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


def _send_otp_via_django_email_backend(email, otp):
    subject = "Your OTP Verification Code"
    message = (
        f"Your OTP is: {otp}. "
        f"It is valid for {settings.OTP_EXPIRY_MINUTES} minutes."
    )
    email_from = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        email_from,
        [email],
        fail_silently=False,
    )


def send_otp_email(email, otp):
    if settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend":
        _send_otp_via_django_email_backend(email, otp)
        return

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
        email_message = EmailMessage(subject, message, email_from, recipient_list)
        email_message.send(fail_silently=False)
    except Exception as exc:
        logger.exception(
            (
                "Gmail OTP send failed for %s using host=%s port=%s tls=%s "
                "user=%s from=%s password=%s"
            ),
            email,
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_USE_TLS,
            host_user,
            settings.DEFAULT_FROM_EMAIL,
            _mask_secret(host_password),
        )
        raise RuntimeError(
            "Unable to send OTP email through Gmail. Check the Gmail address, "
            "app password, and SMTP access."
        ) from exc
