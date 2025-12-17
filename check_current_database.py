#!/usr/bin/env python
"""
Quick script to check which database is currently being used
and list all users in the database.
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.db import connection
from accounts.models import CustomUser

def check_database():
    print("=== DATABASE CONFIGURATION CHECK ===")
    
    # Check database engine
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    
    print(f"Database Engine: {db_engine}")
    print(f"Database Name: {db_name}")
    
    if 'sqlite' in db_engine:
        print(f"SQLite Database Path: {db_name}")
    elif 'mysql' in db_engine:
        print(f"MySQL Database: {settings.DATABASES['default'].get('HOST', 'localhost')}:{settings.DATABASES['default'].get('PORT', 3306)}")
    elif 'postgresql' in db_engine:
        print(f"PostgreSQL Database: {settings.DATABASES['default'].get('HOST', 'localhost')}:{settings.DATABASES['default'].get('PORT', 5432)}")
    
    print("\n=== DATABASE CONNECTION TEST ===")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    print("\n=== USER ACCOUNTS CHECK ===")
    try:
        # Count total users
        total_users = CustomUser.objects.count()
        print(f"Total users in database: {total_users}")
        
        if total_users > 0:
            print("\nRecent users:")
            recent_users = CustomUser.objects.order_by('-date_joined')[:5]
            for user in recent_users:
                print(f"  - {user.username} (Email: {user.email or 'No email'}) - Joined: {user.date_joined}")
        else:
            print("No users found in database!")
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    check_database()