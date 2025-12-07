#!/usr/bin/env python3
"""
EcoLearn Platform Setup Script
This script sets up the development environment and initializes the database.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up the virtual environment and install dependencies."""
    print("Setting up EcoLearn development environment...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_database():
    """Set up the database with migrations."""
    print("\nSetting up database...")
    
    # Use the virtual environment's Python
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{python_cmd} manage.py makemigrations", "Creating migrations"):
        return False
    
    if not run_command(f"{python_cmd} manage.py migrate", "Running migrations"):
        return False
    
    return True

def create_superuser():
    """Create a superuser account."""
    print("\nCreating superuser account...")
    
    # Use the virtual environment's Python
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Create superuser using Django shell
    create_user_script = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    admin_user = User.objects.create_superuser('admin', 'admin@ecolearn.zm', 'admin123', preferred_language='en')
    admin_user.is_verified = True
    admin_user.save()
    print('✓ Superuser created: admin/admin123')
else:
    print('✓ Superuser already exists')
"""
    
    # Write script to file and execute
    with open('temp_create_user.py', 'w') as f:
        f.write(create_user_script)
    
    result = run_command(f"{python_cmd} manage.py shell < temp_create_user.py", "Creating superuser")
    
    # Clean up
    if os.path.exists('temp_create_user.py'):
        os.remove('temp_create_user.py')
    
    return result

def create_sample_data():
    """Create sample data for testing."""
    print("\nCreating sample data...")
    
    # Use the virtual environment's Python
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Create sample data script
    sample_data_script = """
from elearning.models import Category
from community.models import ForumCategory  
from payments.models import PaymentProvider, PaymentPlan

# Create learning categories
categories = [
    {'name': 'Waste Management', 'name_bem': 'Ukupangila Ubwafya', 'name_ny': 'Kasamalidwe ka Zinyalala'},
    {'name': 'Recycling', 'name_bem': 'Ukubwezeshapo', 'name_ny': 'Kubwezeranso'},
    {'name': 'Environmental Protection', 'name_bem': 'Ukuteteka Chialo', 'name_ny': 'Kuteteza Chilengedwe'},
]

for cat_data in categories:
    category, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
    if created:
        print(f'Created category: {category.name}')

# Create forum categories
forum_categories = [
    {'name': 'General Discussion', 'name_bem': 'Ukwishanya Konse', 'name_ny': 'Zokambirana Zonse'},
    {'name': 'Waste Management Tips', 'name_bem': 'Malangizo ya Ubwafya', 'name_ny': 'Malangizo a Zinyalala'},
]

for forum_data in forum_categories:
    forum_cat, created = ForumCategory.objects.get_or_create(name=forum_data['name'], defaults=forum_data)
    if created:
        print(f'Created forum category: {forum_cat.name}')

# Create payment providers
providers = [
    {'name': 'MTN Mobile Money', 'display_name': 'MTN MoMo', 'is_active': True},
    {'name': 'Airtel Money', 'display_name': 'Airtel Money', 'is_active': True},
    {'name': 'Zamtel Kwacha', 'display_name': 'Zamtel Kwacha', 'is_active': True},
]

for provider_data in providers:
    provider, created = PaymentProvider.objects.get_or_create(name=provider_data['name'], defaults=provider_data)
    if created:
        print(f'Created payment provider: {provider.name}')

# Create payment plans
plans = [
    {'name': 'Basic Plan', 'description': 'Access to basic environmental courses', 'price': 50.00, 'duration_days': 30},
    {'name': 'Premium Plan', 'description': 'Full access to all features', 'price': 100.00, 'duration_days': 30},
]

for plan_data in plans:
    plan, created = PaymentPlan.objects.get_or_create(name=plan_data['name'], defaults=plan_data)
    if created:
        print(f'Created payment plan: {plan.name}')

print('✓ Sample data created successfully')
"""
    
    # Write script to file and execute
    with open('temp_sample_data.py', 'w') as f:
        f.write(sample_data_script)
    
    result = run_command(f"{python_cmd} manage.py shell < temp_sample_data.py", "Creating sample data")
    
    # Clean up
    if os.path.exists('temp_sample_data.py'):
        os.remove('temp_sample_data.py')
    
    return result

def main():
    """Main setup function."""
    print("=" * 50)
    print("EcoLearn Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Setup steps
    steps = [
        setup_environment,
        setup_database,
        create_superuser,
        create_sample_data
    ]
    
    for step in steps:
        if not step():
            print(f"\n✗ Setup failed at step: {step.__name__}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ EcoLearn setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the development server:")
    print("   python manage.py runserver")
    print("3. Visit http://127.0.0.1:8000 to see your application")
    print("4. Admin panel: http://127.0.0.1:8000/admin")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n⚠️  Remember to:")
    print("- Change the default admin password")
    print("- Configure your .env file with API keys")
    print("- Set up SMS and payment gateway credentials")

if __name__ == "__main__":
    main()
