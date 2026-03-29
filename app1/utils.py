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

RESEND_PLACEHOLDERS = {
    "",
    "your-resend-api-key",
}

RESEND_TEST_SENDER = "onboarding@resend.dev"

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


def _send_otp_via_resend(email, otp):
    api_key = settings.RESEND_API_KEY
    if api_key in RESEND_PLACEHOLDERS:
        raise ImproperlyConfigured(
            "Resend is not configured. Set RESEND_API_KEY in your environment."
        )

    if not settings.DEFAULT_FROM_EMAIL:
        raise ImproperlyConfigured(
            "DEFAULT_FROM_EMAIL is not configured. Set it to your verified Resend sender."
        )

    if settings.DEFAULT_FROM_EMAIL.strip().lower() == RESEND_TEST_SENDER:
        raise ImproperlyConfigured(
            "Resend test sender cannot deliver production OTP emails. "
            "Replace DEFAULT_FROM_EMAIL with a verified sender from your Resend domain."
        )

    response = requests.post(
        settings.RESEND_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [email],
            "subject": "Your OTP Verification Code",
            "text": (
                f"Your OTP is: {otp}. "
                f"It is valid for {settings.OTP_EXPIRY_MINUTES} minutes."
            ),
        },
        timeout=settings.EMAIL_TIMEOUT,
    )

    if response.status_code >= 400:
        logger.error("Resend OTP send failed: %s", response.text)
        response_body = response.text.lower()
        if "onboarding@resend.dev" in response_body or "verify a domain" in response_body:
            raise RuntimeError(
                "Resend rejected the sender address. Use a verified sender/domain "
                "for DEFAULT_FROM_EMAIL instead of onboarding@resend.dev."
            )
        raise RuntimeError(
            "Unable to send OTP email through Resend. Check the API key and sender configuration."
        )


def send_otp_email(email, otp):
    if settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend":
        _send_otp_via_django_email_backend(email, otp)
        return

    provider = settings.OTP_EMAIL_PROVIDER
    if provider == "resend":
        _send_otp_via_resend(email, otp)
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
