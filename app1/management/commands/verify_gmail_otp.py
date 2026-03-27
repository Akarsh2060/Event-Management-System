from django.core.management.base import BaseCommand, CommandError

from app1.utils import send_otp_email


class Command(BaseCommand):
    help = "Send a test OTP email using the configured Gmail SMTP settings."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Recipient email address")
        parser.add_argument(
            "--otp",
            default="123456",
            help="OTP value to send in the verification email",
        )

    def handle(self, *args, **options):
        email = options["email"]
        otp = options["otp"]

        try:
            send_otp_email(email, otp)
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"OTP email sent successfully to {email} with OTP {otp}."
            )
        )
