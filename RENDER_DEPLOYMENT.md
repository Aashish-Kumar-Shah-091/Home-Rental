# Render Deployment Guide for Home Rental Application

## Step 1: Prepare Your Repository

1. Make sure all your code is pushed to GitHub
2. Ensure `.env` file is in `.gitignore` (it should be)
3. Verify `requirements.txt` is up to date

## Step 2: Create Render Account & Service

1. Go to [render.com](https://render.com) and sign up/login
2. Connect your GitHub repository
3. Create a new service from the `render.yaml` blueprint

## Step 3: Environment Variables Setup

In Render Dashboard, set the following environment variables:

### Critical (Must Set):
- **SECRET_KEY**: Generate a new secret key:
  ```
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- **ALLOWED_HOSTS**: Your Render domain (e.g., `home-rental.onrender.com`)
- **EMAIL_HOST_USER**: Your Gmail address
- **EMAIL_HOST_PASSWORD**: Gmail App Password (NOT your regular password)
- **ESEWA_SECRET_KEY**: Your eSewa merchant secret key

### Auto-configured (via render.yaml):
- DATABASE_URL and related DB variables (PostgreSQL)
- CHANNEL_REDIS_URL (Redis service)
- DEBUG=false (for production)

## Step 4: Configure Payment URLs

Update your payment success/failure URLs after deployment:
```
SUCCESS_URL=https://[your-render-domain].onrender.com/payment/success/
FAILURE_URL=https://[your-render-domain].onrender.com/payment/failure/
```

## Step 5: First Deployment

1. Deploy will automatically run:
   - `pip install -r requirements.txt`
   - `python manage.py collectstatic --no-input`
   - `python manage.py migrate`
   
2. Monitor the deployment logs in Render Dashboard

## Step 6: Post-Deployment Setup

1. Create a superuser for Django admin:
   ```
   Visit the Render Shell and run:
   python manage.py createsuperuser
   ```

2. Access admin at: `https://[your-render-domain].onrender.com/admin/`

## Step 7: Custom Domain (Optional)

1. In Render Dashboard, go to your service settings
2. Add your custom domain
3. Follow Render's DNS instructions

## Troubleshooting

### Static Files Not Loading
- Check that `STATIC_URL` and `STATIC_ROOT` are correct in settings.py
- Clear browser cache (Ctrl+Shift+Delete)

### Database Connection Issues
- Verify DATABASE_URL environment variable is set
- Check PostgreSQL credentials in render.yaml

### WebSocket Issues
- Ensure Redis service is created and running
- Verify CHANNEL_REDIS_URL is set

### Email Not Sending
- Use Gmail App Password (NOT your regular password)
- Enable "Less secure app access" if using 2FA not set up
- Check spam folder first

## Important Files for Deployment

- `render.yaml` - Main deployment configuration
- `build.sh` - Build script (automatic)
- `.env.example` - Environment variable template
- `requirements.txt` - Python dependencies
- `Procfile` - Alternative configuration (render.yaml takes precedence)

## Common Commands via Render Shell

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Check database connection
python manage.py dbshell

# Run custom management commands
python manage.py [command_name]
```

## Performance Tips

1. Enable Redis caching if not using for WebSockets
2. Use PostgreSQL proper indexing (check migrations)
3. Monitor logs for slow queries
4. Consider CDN for media files

## Security Checklist

- [ ] SECRET_KEY changed from development key
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured with your domain
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] Email credentials secure
- [ ] Database password strong
- [ ] HTTPS enforced (automatic on Render)

## Support & Resources

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
- Channels Deployment: https://channels.readthedocs.io/en/latest/deploying.html
