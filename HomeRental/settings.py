"""
Django settings for HomeRental project.
Configuration for home rental web application.
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse
import cloudinary


from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

# ===== CLOUDINARY INITIALIZATION =====
# Initialize Cloudinary early so CloudinaryField can use it


cloudinary.config(
    cloud_name=os.getenv("dbekyt3g2"),
    api_key=os.getenv("642252122754475"),
    api_secret=os.getenv("gMImWB_gcj9RGFPFq3VuqJWO-io")
)

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# ===== SECURITY SETTINGS =====
DEBUG = True

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-only-change-me"
    else:
        raise ImproperlyConfigured("SECRET_KEY environment variable must be set when DEBUG is False.")


# Dynamic hosts: ALLOWED_HOSTS env + Render hostname + safe defaults
allowed_hosts = env_list("ALLOWED_HOSTS")
render_external_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_external_hostname:
    allowed_hosts.append(render_external_hostname)

if not allowed_hosts:
    allowed_hosts.extend(["localhost", "127.0.0.1", "[::1]"])

# Prevent DisallowedHost in Render if ALLOWED_HOSTS is not fully configured yet
if not DEBUG:
    allowed_hosts.append(".onrender.com")

normalized_hosts = []
for host in allowed_hosts:
    cleaned = host.replace("https://", "").replace("http://", "").split("/")[0].strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        normalized_hosts.append(cleaned)
        continue
    normalized_hosts.append(cleaned.split(":")[0])

ALLOWED_HOSTS = sorted({h for h in normalized_hosts if h})


# Dynamic CSRF trusted origins
csrf_trusted_origins = env_list("CSRF_TRUSTED_ORIGINS")
for host in ALLOWED_HOSTS:
    if host.startswith("."):
        csrf_trusted_origins.append(f"https://*{host}")
    elif host in {"localhost", "127.0.0.1", "[::1]"}:
        csrf_trusted_origins.extend([f"http://{host}", f"https://{host}"])
    else:
        csrf_trusted_origins.append(f"https://{host}")

CSRF_TRUSTED_ORIGINS = sorted({origin for origin in csrf_trusted_origins if origin})

# Media backend: local | s3 | cloudinary
MEDIA_STORAGE_BACKEND = os.getenv("MEDIA_STORAGE_BACKEND", "local").strip().lower()
if MEDIA_STORAGE_BACKEND not in {"local", "s3", "cloudinary"}:
    raise ImproperlyConfigured(
        "MEDIA_STORAGE_BACKEND must be one of: local, s3, cloudinary."
    )


# ===== INSTALLED APPLICATIONS =====
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "daphne",
    "django.contrib.staticfiles",
    "channels",
    "chat",
    "home",
    "payments",
]

if MEDIA_STORAGE_BACKEND == "s3":
    INSTALLED_APPS.append("storages")
elif MEDIA_STORAGE_BACKEND == "cloudinary":
    INSTALLED_APPS.extend(["cloudinary_storage", "cloudinary"])


# ===== MIDDLEWARE CONFIGURATION =====
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ===== URL / APP ENTRYPOINTS =====
ROOT_URLCONF = "HomeRental.urls"
ASGI_APPLICATION = "HomeRental.asgi.application"
WSGI_APPLICATION = "HomeRental.wsgi.application"  # Gunicorn uses this


# ===== TEMPLATE CONFIGURATION =====
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.unread_notifications_count",
            ],
        },
    },
]


# ===== CHANNELS / WEBSOCKETS =====
CHANNEL_REDIS_URL = os.getenv("CHANNEL_REDIS_URL", "").strip()
has_channels_redis = False
try:
    import channels_redis  # noqa: F401
    has_channels_redis = True
except ImportError:
    has_channels_redis = False

if CHANNEL_REDIS_URL and has_channels_redis:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [CHANNEL_REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }


# ===== DATABASE CONFIGURATION =====
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DB_ENGINE = os.getenv("DB_ENGINE", "").strip().lower()
DB_NAME = os.getenv("DB_NAME", "").strip()
DB_USER = os.getenv("DB_USER", "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_HOST = os.getenv("DB_HOST", "").strip()
DB_PORT = os.getenv("DB_PORT", "").strip()

if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    scheme = parsed.scheme.lower()

    if scheme in {"postgres", "postgresql", "pgsql", "postgis"}:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": unquote(parsed.path.lstrip("/")),
                "USER": unquote(parsed.username or ""),
                "PASSWORD": unquote(parsed.password or ""),
                "HOST": parsed.hostname or "",
                "PORT": str(parsed.port or "5432"),
                "OPTIONS": {"sslmode": "require"} if not DEBUG else {},
                "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
                "CONN_HEALTH_CHECKS": True,
            }
        }
    elif scheme in {"mysql", "mysql2"}:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": unquote(parsed.path.lstrip("/")),
                "USER": unquote(parsed.username or ""),
                "PASSWORD": unquote(parsed.password or ""),
                "HOST": parsed.hostname or "127.0.0.1",
                "PORT": str(parsed.port or "3306"),
                "OPTIONS": {"charset": "utf8mb4"},
            }
        }
    else:
        raise ImproperlyConfigured(f"Unsupported DATABASE_URL scheme: {scheme}")

elif DB_ENGINE in {"postgresql", "django.db.backends.postgresql", "psycopg2"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME or "home_rental_db",
            "USER": DB_USER or "postgres",
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST or "localhost",
            "PORT": DB_PORT or "5432",
            "OPTIONS": {"sslmode": "require"} if (not DEBUG and DB_HOST) else {},
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
            "CONN_HEALTH_CHECKS": True,
        }
    }

elif DB_ENGINE in {"mysql", "django.db.backends.mysql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": DB_NAME or "home_rental",
            "USER": DB_USER or "root",
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST or "127.0.0.1",
            "PORT": DB_PORT or "3306",
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ===== PASSWORD VALIDATION =====
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ===== INTERNATIONALIZATION SETTINGS =====
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ===== STATIC / MEDIA CONFIGURATION =====
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

USE_MANIFEST_STATIC_FILES = env_bool("USE_MANIFEST_STATIC_FILES", False)
if USE_MANIFEST_STATIC_FILES:
    staticfiles_backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    # Safer default on platforms where collectstatic/manifest may drift; avoids 500
    # from missing manifest entries while keeping compressed static serving.
    staticfiles_backend = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))
SERVE_MEDIA_FILES = env_bool(
    "SERVE_MEDIA_FILES",
    DEBUG or MEDIA_STORAGE_BACKEND == "local",
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": staticfiles_backend,
    },
}
# Avoid 500s if a stale/missing manifest occurs during rollout; static files may
# still 404, but pages won't crash.
WHITENOISE_MANIFEST_STRICT = False

if MEDIA_STORAGE_BACKEND == "s3":
    aws_bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
    if not aws_bucket_name:
        raise ImproperlyConfigured(
            "AWS_STORAGE_BUCKET_NAME is required when MEDIA_STORAGE_BACKEND=s3."
        )

    aws_region = os.getenv("AWS_S3_REGION_NAME", "").strip()
    aws_custom_domain = os.getenv("AWS_S3_CUSTOM_DOMAIN", "").strip()
    aws_media_location = os.getenv("AWS_MEDIA_LOCATION", "media").strip().strip("/")

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": aws_bucket_name,
            "region_name": aws_region or None,
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", "").strip() or None,
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", "").strip() or None,
            "default_acl": None,
            "file_overwrite": False,
            "querystring_auth": env_bool("AWS_QUERYSTRING_AUTH", False),
            "location": aws_media_location,
            "custom_domain": aws_custom_domain or None,
        },
    }

    if aws_custom_domain:
        MEDIA_URL = f"https://{aws_custom_domain}/{aws_media_location}/"
    elif aws_region:
        MEDIA_URL = f"https://{aws_bucket_name}.s3.{aws_region}.amazonaws.com/{aws_media_location}/"
    else:
        MEDIA_URL = f"https://{aws_bucket_name}.s3.amazonaws.com/{aws_media_location}/"

elif MEDIA_STORAGE_BACKEND == "cloudinary":
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key = os.getenv("CLOUDINARY_API_KEY", "").strip()
    api_secret = os.getenv("CLOUDINARY_API_SECRET", "").strip()

    if not all([cloud_name, api_key, api_secret]):
        raise ImproperlyConfigured(
            "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET are required "
            "when MEDIA_STORAGE_BACKEND=cloudinary."
        )

    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": cloud_name,
        "API_KEY": api_key,
        "API_SECRET": api_secret,
    }
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }
    MEDIA_URL = f"https://res.cloudinary.com/{cloud_name}/"


# ===== AUTHENTICATION SETTINGS =====
LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/home/"
LOGOUT_REDIRECT_URL = "/home/"


# ===== EMAIL SETTINGS =====
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)


# ===== PAYMENT SETTINGS =====
ESEWA_MERCHANT_ID = os.getenv("ESEWA_MERCHANT_ID", "EPAYTEST")
ESEWA_SECRET_KEY = os.getenv("ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q")
ESEWA_SIGNED_FIELD_NAMES = os.getenv(
    "ESEWA_SIGNED_FIELD_NAMES",
    "total_amount,transaction_uuid,product_code",
)
ESEWA_FORM_URL = os.getenv(
    "ESEWA_FORM_URL",
    "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
)
SUCCESS_URL = os.getenv("SUCCESS_URL", "http://127.0.0.1:8000/payment/success/")
FAILURE_URL = os.getenv("FAILURE_URL", "http://127.0.0.1:8000/payment/failure/")


# ===== PRODUCTION SECURITY SETTINGS =====
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("SECURE_REFERRER_POLICY", "same-origin")
X_FRAME_OPTIONS = os.getenv("X_FRAME_OPTIONS", "DENY")


# ===== DEFAULT PRIMARY KEY FIELD TYPE =====
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"