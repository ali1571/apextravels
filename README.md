# Apex Tour Travel (Discontinued by the Client)

Website for a party bus / limo / tour travel business, live at [apextourtravel.com](https://apextourtravel.com). Built as a custom Django application rather than a CMS.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | Django templates + [Tailwind CSS / custom CSS] |
| Database | [PostgreSQL via Railway / SQLite] |
| Image storage | Supabase Storage |
| Transactional email | Resend |
| Hosting | Railway |
| Domain / DNS | [registrar] → Railway custom domain |

## Features

- Public-facing pages: [home, fleet, services, about, contact, etc.]
- Inquiry / contact form that sends email notifications via Resend
- Images served from Supabase Storage buckets
- [Admin panel via Django admin for managing content]
- Mobile-responsive layout

## Project Structure

```
apextravels/
├── manage.py
├── [project_name]/        # settings, urls, wsgi
├── [app_name]/            # views, models, forms, templates
├── templates/
├── static/
├── requirements.txt
└── [Procfile / railway.json]
```

## Environment Variables

```
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
DATABASE_URL=
RESEND_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_BUCKET=
```

## Local Setup

```bash
git clone <repo-url>
cd apextravels
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in values
python manage.py migrate
python manage.py runserver
```

## Deployment

Deployed on Railway:
1. Connect the GitHub repo to a Railway project
2. Set the environment variables above in the Railway dashboard
3. Railway builds and deploys on every push to `main`
4. Custom domain is attached in Railway, with DNS records (CNAME/A) set at the registrar

## Integrations

- **Resend:** sends inquiry notifications; requires domain verification (SPF/DKIM) on the sending domain
- **Supabase:** used purely as object storage for images; media isn't stored on the Railway filesystem, since it's ephemeral

## Notes

- This is a custom Django build, so content and layout changes are made in code, not through a CMS like WordPress.
- Private client project. [License / ownership info]
