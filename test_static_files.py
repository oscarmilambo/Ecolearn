"""
Quick test to verify static files configuration
"""
import os
from pathlib import Path

# Check if images exist
images_path = Path('static/images')
print("=" * 50)
print("STATIC FILES CHECK")
print("=" * 50)

if images_path.exists():
    print(f"✅ static/images folder exists")
    images = list(images_path.glob('*.*'))
    print(f"✅ Found {len(images)} files in static/images/")
    print("\nImages found:")
    for img in images:
        print(f"  - {img.name}")
else:
    print("❌ static/images folder NOT found")

print("\n" + "=" * 50)
print("REQUIRED IMAGES FOR LANDING PAGE")
print("=" * 50)

required_images = [
    'zambia_c.jpg',
    'comunty_action.jpg'  # Note: typo in filename
]

for img in required_images:
    img_path = images_path / img
    if img_path.exists():
        print(f"✅ {img} - FOUND")
    else:
        print(f"❌ {img} - MISSING")

print("\n" + "=" * 50)
print("NEXT STEPS")
print("=" * 50)
print("1. Run: python manage.py collectstatic --noinput")
print("2. Restart your Django server")
print("3. Hard refresh your browser (Ctrl+F5)")
print("=" * 50)
