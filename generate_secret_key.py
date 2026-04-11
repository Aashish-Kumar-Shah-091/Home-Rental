#!/usr/bin/env python
"""
Utility script to generate Django SECRET_KEY for production deployment.
 
Usage:
    python generate_secret_key.py
    
This will output a secure random SECRET_KEY suitable for production.
Copy this value and set it as SECRET_KEY environment variable in Render dashboard.
"""

from django.core.management.utils import get_random_secret_key


def main():
    """Generate and display a new SECRET_KEY"""
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("NEW DJANGO SECRET KEY FOR PRODUCTION")
    print("="*70)
    print(f"\n{secret_key}\n")
    print("="*70)
    print("INSTRUCTIONS:")
    print("="*70)
    print("1. Copy the SECRET_KEY above (without quotes)")
    print("2. Go to Render Dashboard → Your Service → Environment")
    print("3. Add new variable:")
    print("   - Key: SECRET_KEY")
    print("   - Value: [paste the key above]")
    print("4. Click 'Save' and Render will redeploy with new SECRET_KEY")
    print("\n⚠️  SECURITY WARNING:")
    print("   - NEVER commit SECRET_KEY to GitHub")
    print("   - NEVER share SECRET_KEY with anyone")
    print("   - This ensures your application stays secure")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
