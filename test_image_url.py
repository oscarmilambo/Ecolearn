"""
Test to see what URL Django generates for the image
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.templatetags.static import static
from django.conf import settings

print("=" * 60)
print("DJANGO STATIC FILES TEST")
print("=" * 60)

print(f"\nDEBUG mode: {settings.DEBUG}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

print("\n" + "=" * 60)
print("IMAGE URL GENERATION TEST")
print("=" * 60)

# Test the image URLs
images = ['images/ghetto.jpg', 'images/zambia_c.jpg']

for img in images:
    url = static(img)
    print(f"\n{img}")
    print(f"  Generated URL: {url}")
    
    # Check if file exists
    from pathlib import Path
    file_path = Path(settings.BASE_DIR) / 'static' / img
    if file_path.exists():
        print(f"  ✅ File exists at: {file_path}")
        print(f"  File size: {file_path.stat().st_size / 1024:.2f} KB")
    else:
        print(f"  ❌ File NOT found at: {file_path}")

print("\n" + "=" * 60)
print("WHAT TO DO NEXT")
print("=" * 60)
print("1. Open your browser")
print("2. Go to: http://127.0.0.1:8000/")
print("3. Press F12 to open Developer Tools")
print("4. Go to 'Network' tab")
print("5. Refresh page (Ctrl+F5)")
print("6. Look for 'ghetto.jpg' in the list")
print("7. Check if it shows 200 (success) or 404 (not found)")
print("=" * 60)
