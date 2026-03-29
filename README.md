# Event Management System

Portfolio-ready Django event booking and management application with OTP-based email verification, booking workflows, payments, and admin dashboards.

## Recommended deployment

Render is the best fit for showcasing this project in a portfolio:

- It supports Django cleanly.
- It gives you a public HTTPS URL quickly.
- It works well with GitHub-based auto-deploys.
- Environment variables stay in the hosting dashboard instead of the repo.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Create a local `.env` using `.env.example` and fill in your real values.

## Production environment variables

Set these in Render, not in GitHub:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_SSLMODE`
- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `SECURE_SSL_REDIRECT=True`

OTP delivery now uses SMTP only. If you deploy on a platform that restricts outbound SMTP, you will need a host that allows SMTP connections or an app-specific mail relay.

## GitHub safety

Sensitive files are ignored in `.gitignore`, including `.env`, local databases, logs, and generated static/media folders.

## Deployment flow

1. Push this repository to GitHub.
2. Create a new Render web service from the repo.
3. Add the production environment variables in the Render dashboard.
4. Trigger the first deploy.
