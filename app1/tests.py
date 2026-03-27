import json

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings

from app1.models import tbl_register


class OtpFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="9876543210",
            email="person@example.com",
            password="secret123",
        )
        self.profile = tbl_register.objects.create(
            user=self.user,
            uname="Person",
            email="person@example.com",
            phone="9876543210",
        )

    def test_register_send_otp_sends_email_and_stores_session(self):
        response = self.client.post(
            "/api/register-send-otp/",
            data=json.dumps(
                {
                    "uname": "New User",
                    "email": "new@example.com",
                    "phone": "9998887776",
                    "password": "secret123",
                    "confirm_password": "secret123",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        self.assertIn("OTP", mail.outbox[0].subject)
        self.assertIn("register_otp", self.client.session)

    def test_login_send_otp_sends_email_and_stores_session(self):
        response = self.client.post(
            "/api/send-otp/",
            data=json.dumps({"identifier": "person@example.com"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["person@example.com"])
        self.assertEqual(self.client.session["login_identifier"], "person@example.com")

    def test_forget_send_otp_sends_email_and_stores_session(self):
        response = self.client.post(
            "/api/send-forget-otp/",
            data=json.dumps({"identifier": "9876543210"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["person@example.com"])
        self.assertEqual(self.client.session["reset_identifier"], "9876543210")

    @override_settings(
        EMAIL_HOST_USER="your-email@gmail.com",
        EMAIL_HOST_PASSWORD="your-app-password",
        DEFAULT_FROM_EMAIL="your-email@gmail.com",
    )
    def test_send_login_otp_returns_helpful_error_for_placeholder_gmail_config(self):
        response = self.client.post(
            "/api/send-otp/",
            data=json.dumps({"identifier": "person@example.com"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("Gmail SMTP is not configured", response.json()["error"])
