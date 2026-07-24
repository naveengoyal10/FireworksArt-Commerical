# Handmade Paintings E‑commerce (Django)

Minimal Django project for selling handmade paintings.

Quick start

1. Create a virtualenv and activate it.
2. Install requirements:

```
pip install -r requirements.txt
```

3. Apply migrations:

```
python manage.py migrate
```

4. Create a superuser:

```
python manage.py createsuperuser
```

5. Run the development server:

```
python manage.py runserver
```

Notes

- Media uploads are stored in `media/` during development.
- This project is a minimal starter: extend payments, product images, and styling as needed.

Environment

- Copy `.env.example` to `.env` and set `SECRET_KEY` and any service credentials (Razorpay/Stripe/DATABASE_URL).

Payments

- Razorpay integration is included. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `.env`.

Deployment

- A sample `deploy/gunicorn.service` and `deploy/nginx.conf` are included to help with production deployment.
- Run `python manage.py collectstatic` and configure your webserver to serve `staticfiles/` and `media/`.
