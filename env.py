import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_ZMKW3T0EUgYo@ep-mute-voice-a26e38xj.eu-central-1.aws.neon.tech/mash_spoke_verse_798216")

os.environ.setdefault("ENV", "dev")

os.environ.setdefault("EMAIL_VERIFICATION", "none")

os.environ.setdefault("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

os.environ.setdefault("DEFAULT_FROM_EMAIL", "no-reply@example.com")

os.environ.setdefault("SECRET_KEY", "9gEJhM<$1NSZnNPM@q>M<Zdy_IK1C,g.eOftrKzNo/MHIQ?~oYo=RpQ8?L")

os.environ.setdefault(
    'CLOUDINARY_URL',
    'cloudinary://<your_api_key>:<your_api_secret>@dk5tufq1l')

os.environ.setdefault(
    'UPLOADTHING_TOKEN', 'eyJhcGlLZXkiOiJza19saXZlXzQ3ZGZiZTZjNTFmOTUyY2EwMmI1OTkwNjllN2FlZmMzOGIxZTFmNjAxM2UyYjMyZTdhZDFhOTZkMWU3MmFkZTEiLCJhcHBJZCI6InRwZjEwcnhtanYiLCJyZWdpb25zIjpbInNlYTEiXX0=')

os.environ.setdefault("DJANGO_EMAIL_HOST", "smtp.sendgrid.net")
os.environ.setdefault("DJANGO_EMAIL_PORT", "587")
os.environ.setdefault("DJANGO_EMAIL_USE_TLS", "true")
os.environ.setdefault("DJANGO_EMAIL_HOST_USER", "email_verification")
os.environ.setdefault("DJANGO_EMAIL_HOST_PASSWORD", "SG.SK67c41bc8d15f2453368f6eb605a5d64b")
os.environ.setdefault("DJANGO_DEFAULT_FROM_EMAIL", "fairytaib@gmail.com")

