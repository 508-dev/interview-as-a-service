# Interview-as-a-Service

A Django + HTMX web application for 508.dev's interview service. Users can browse interviewers, book sessions via cal.com, pay via Stripe, and upload resumes. Interviewers have an admin panel to manage their profile and view bookings.

## Tech Stack

- **Backend**: Django 5.1, PostgreSQL
- **Frontend**: HTMX, vanilla CSS (no frameworks)
- **Payments**: Stripe Checkout
- **Scheduling**: Cal.com embed
- **Storage**: MinIO (S3-compatible) for file uploads
- **Testing**: pytest, pytest-django, factory-boy, Playwright

## Project Structure

```
interview-as-a-service/
├── interview_service/     # Django project settings
├── accounts/              # Authentication (login/logout)
├── interviewers/          # Interviewer profiles
├── bookings/              # Booking flow + Stripe integration
├── dashboard/             # Interviewer admin panel
├── pages/                 # Static pages (homepage)
├── templates/             # HTML templates
├── static/                # CSS, JS assets
├── tests/                 # pytest unit tests
└── e2e/                   # Playwright E2E tests
```

---

## Development Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Node.js (optional, for TypeScript)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd interview-as-a-service

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (for development, defaults work fine)
```

Key variables for development:
```env
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
POSTGRES_DB=interview_service
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 3. Start Database Services (Docker)

```bash
# Start PostgreSQL and MinIO
docker compose -f docker-compose.dev.yml up -d

# Verify services are running
docker compose -f docker-compose.dev.yml ps
```

This starts:
- **PostgreSQL** on `localhost:5432`
- **MinIO** on `localhost:9000` (API) and `localhost:9001` (Console)

MinIO Console credentials: `minioadmin` / `minioadmin`

### 4. Initialize Django

```bash
# Run database migrations
python manage.py migrate

# Create a superuser for Django admin
python manage.py createsuperuser

# Collect static files (optional in dev)
python manage.py collectstatic --noinput
```

### 5. Load Sample Data (Optional)

```bash
# Open Django shell to create test data
python manage.py shell

# In the shell:
from django.contrib.auth.models import User
from interviewers.models import Interviewer, Technology, InterviewSubject

# Create technologies
python = Technology.objects.create(name="Python", slug="python")
react = Technology.objects.create(name="React", slug="react")
system_design = InterviewSubject.objects.create(name="System Design", slug="system-design")

# Create an interviewer
user = User.objects.create_user("interviewer1", "interviewer@example.com", "testpass123")
user.first_name = "Jane"
user.last_name = "Doe"
user.save()

interviewer = Interviewer.objects.create(
    user=user,
    bio="10 years at Google, expert in distributed systems.",
    cal_event_type_id="jane-doe/interview",
    hourly_rate=150.00,
    companies="Google, Meta, Stripe"
)
interviewer.technologies.add(python, react)
interviewer.subjects.add(system_design)
```

### 6. Run the Development Server

```bash
# Start Django development server with hot reload
python manage.py runserver
```

The application is now available at: **http://localhost:8000**

- Homepage: http://localhost:8000/
- Interviewers: http://localhost:8000/interviewers/
- Django Admin: http://localhost:8000/admin/
- Interviewer Login: http://localhost:8000/accounts/login/

### 7. Stripe Webhook Testing (Development)

To test Stripe webhooks locally, use the Stripe CLI:

```bash
# Install Stripe CLI (macOS)
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:8000/bookings/webhook/stripe/

# Note the webhook signing secret and add it to .env
# STRIPE_WEBHOOK_SECRET=whsec_...
```

### Stopping Development Services

```bash
# Stop the Django server
Ctrl+C

# Stop Docker services
docker compose -f docker-compose.dev.yml down

# Stop and remove volumes (clears database)
docker compose -f docker-compose.dev.yml down -v
```

---

## Running Tests

### Unit Tests (pytest)

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### E2E Tests (Playwright)

```bash
# Install Playwright browsers (first time only)
playwright install

# Start the development server in one terminal
python manage.py runserver

# Run E2E tests in another terminal
pytest e2e/

# Run specific E2E test
pytest e2e/test_homepage.py

# Run in headed mode (see the browser)
pytest e2e/ --headed
```

---

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- Domain name with SSL certificate
- Stripe account (live keys)
- Cal.com account
- SMTP server for emails

### 1. Configure Production Environment

```bash
# Copy and edit the environment file
cp .env.example .env
```

Edit `.env` with production values:

```env
# Django
SECRET_KEY=your-secure-random-secret-key
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
POSTGRES_DB=interview_service
POSTGRES_USER=interview_user
POSTGRES_PASSWORD=secure-database-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# MinIO / S3 Storage
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
MINIO_BUCKET_NAME=interview-service
MINIO_ENDPOINT_URL=http://minio:9000

# Stripe (Live keys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Cal.com
CAL_COM_API_KEY=your-cal-com-api-key

# Email (SMTP)
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@yourdomain.com
EMAIL_HOST_PASSWORD=your-smtp-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security
SECURE_SSL_REDIRECT=true
```

### 2. Build and Start Production Stack

```bash
# Build the Docker images
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check service status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f web
```

This starts:
- **web**: Django application (Gunicorn)
- **db**: PostgreSQL database
- **minio**: MinIO object storage
- **nginx**: Reverse proxy serving static files

### 3. Initialize Production Database

```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files (done automatically in Dockerfile, but can re-run)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 4. Configure Stripe Webhooks

1. Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Add endpoint: `https://yourdomain.com/bookings/webhook/stripe/`
3. Select events: `checkout.session.completed`
4. Copy the signing secret to `STRIPE_WEBHOOK_SECRET` in `.env`
5. Restart the web service:
   ```bash
   docker compose -f docker-compose.prod.yml restart web
   ```

### 5. SSL/HTTPS Configuration

The included `nginx.conf` is basic. For production with SSL:

1. **Option A**: Use a reverse proxy like Cloudflare or AWS ALB
2. **Option B**: Add Let's Encrypt with certbot:

```bash
# Install certbot and obtain certificate
# Then update nginx.conf with SSL configuration
```

Example SSL nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /static/ {
        alias /app/staticfiles/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Production Management Commands

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down

# Update and redeploy
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Database backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

---

## Architecture Overview

### Request Flow

1. User visits homepage → `pages/views.py:home`
2. User browses interviewers → `interviewers/views.py:interviewer_list`
3. User clicks interviewer card → HTMX loads modal via `interviewer_detail_modal`
4. User clicks "Book Now" → `bookings/views.py:booking_start` (Cal.com embed)
5. User selects time → `bookings/views.py:booking_form`
6. User submits form → `bookings/views.py:create_booking` → Stripe Checkout
7. Payment success → Stripe webhook → `bookings/webhooks.py:stripe_webhook`
8. Booking confirmed → Emails sent to customer and interviewer

### Key Files

| File | Purpose |
|------|---------|
| `interviewers/models.py` | Interviewer, Technology, InterviewSubject models |
| `bookings/models.py` | Booking model with status workflow |
| `bookings/stripe.py` | Stripe checkout session creation |
| `bookings/webhooks.py` | Stripe webhook handler |
| `bookings/emails.py` | Email notification functions |
| `dashboard/views.py` | Interviewer dashboard views |
| `templates/base.html` | Base template with HTMX setup |
| `static/css/styles.css` | All CSS styles |

---

## Troubleshooting

### Database connection refused
```bash
# Ensure PostgreSQL is running
docker compose -f docker-compose.dev.yml ps

# Check PostgreSQL logs
docker compose -f docker-compose.dev.yml logs db
```

### Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# In production, ensure nginx is serving /static/
```

### Stripe webhooks not working
```bash
# Check webhook endpoint is accessible
curl -X POST https://yourdomain.com/bookings/webhook/stripe/

# Verify STRIPE_WEBHOOK_SECRET is set correctly
# Check Stripe dashboard for webhook delivery attempts
```

### MinIO bucket not created
```bash
# The createbucket service should auto-create it
# Manually create if needed:
docker compose -f docker-compose.dev.yml exec minio mc mb local/interview-service
```

---

## License

See [LICENSE](LICENSE) file.
