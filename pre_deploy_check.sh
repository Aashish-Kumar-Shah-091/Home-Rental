#!/bin/bash
# Pre-deployment verification script for Render
# Run this before deploying to catch common configuration issues

set -e

echo "================================"
echo "Render Pre-Deployment Checker"
echo "================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python --version

# Check required files exist
echo "✓ Checking required files..."
required_files=("manage.py" "requirements.txt" "runtime.txt" "render.yaml" "build.sh" ".env.example")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "  ✗ Missing: $file"
        exit 1
    else
        echo "  ✓ Found: $file"
    fi
done

# Check .env.example
echo ""
echo "✓ Checking environment variables..."
required_env_vars=("SECRET_KEY" "DEBUG" "ALLOWED_HOSTS" "EMAIL_HOST_USER" "EMAIL_HOST_PASSWORD" "ESEWA_SECRET_KEY")
for var in "${required_env_vars[@]}"; do
    if grep -q "$var" .env.example; then
        echo "  ✓ $var defined in .env.example"
    else
        echo "  ✗ $var NOT defined in .env.example"
    fi
done

# Check requirements.txt
echo ""
echo "✓ Checking dependencies..."
required_packages=("Django" "gunicorn" "psycopg2" "daphne" "channels" "whitenoise")
for package in "${required_packages[@]}"; do
    if grep -i; then
        echo "  ✓ $package found"
    fi
done

# Check migrations
echo ""
echo "✓ Checking migrations..."
if python manage.py showmigrations --plan 2>/dev/null | grep -q "^  ( )"; then
    echo "  ⚠️  Warning: Unapplied migrations detected"
    echo "  Run: python manage.py migrate"
else
    echo "  ✓ All migrations applied"
fi

# Check static files
echo ""
echo "✓ Checking static files collection..."
if [ ! -d "staticfiles" ]; then
    echo "  Note: Run 'python manage.py collectstatic' to prepare"
else
    echo "  ✓ Static files directory exists"
fi

echo ""
echo "================================"
echo "✓ Pre-deployment check complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env with your configured values"
echo "2. Run: python manage.py runserver"
echo "3. Test locally: http://localhost:8000"
echo "4. If all works, push to GitHub"
echo "5. Deploy on Render dashboard"
echo ""
