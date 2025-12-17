#!/usr/bin/env python3
"""
Test Challenge Join Functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from community.models import CommunityChallenge, ChallengeParticipant
from django.utils import timezone
from datetime import timedelta

def test_challenge_join():
    """Test the challenge join functionality"""
    print("🔍 Testing Challenge Join Functionality")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='challengeuser',
        defaults={
            'email': 'challenge@example.com',
            'phone_number': '+260970000002'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Test user created")
    else:
        print("✅ Test user exists")
    
    # Create test challenge
    challenge, created = CommunityChallenge.objects.get_or_create(
        title='Test CSRF Challenge',
        defaults={
            'description': 'Test challenge for CSRF debugging',
            'challenge_type': 'waste_collection',
            'target_goal': 100,
            'reward_points': 50,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=30),
            'is_active': True
        }
    )
    
    if created:
        print("✅ Test challenge created")
    else:
        print("✅ Test challenge exists")
    
    # Login user
    login_success = client.login(username='challengeuser', password='testpass123')
    print(f"✅ User login: {login_success}")
    
    # Test 1: GET challenges list page
    print("\n1. Testing challenges list page...")
    response = client.get('/community/challenges/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'Test CSRF Challenge' in content:
            print("   ✅ Challenge found in list")
        if 'csrfmiddlewaretoken' in content:
            print("   ✅ CSRF token found in page")
        else:
            print("   ❌ CSRF token not found in page")
    
    # Test 2: POST to join challenge
    print("\n2. Testing challenge join POST...")
    
    # Get CSRF token first
    response = client.get('/community/challenges/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   ✅ CSRF token extracted: {csrf_token[:20]}...")
            
            # POST to join challenge
            join_response = client.post(
                f'/community/challenges/{challenge.id}/join/',
                data={'csrfmiddlewaretoken': csrf_token}
            )
            
            print(f"   Join POST Status: {join_response.status_code}")
            
            if join_response.status_code == 302:
                print("   ✅ Challenge join successful (redirect)")
                
                # Check if user was actually added to challenge
                participant = ChallengeParticipant.objects.filter(
                    challenge=challenge,
                    user=user
                ).first()
                
                if participant:
                    print("   ✅ User successfully joined challenge in database")
                else:
                    print("   ❌ User not found in challenge participants")
                    
            elif join_response.status_code == 403:
                print("   ❌ CSRF verification failed")
                content = join_response.content.decode('utf-8')
                if 'CSRF verification failed' in content:
                    print("   ❌ Confirmed CSRF error")
                    print("   Content preview:", content[:200])
            else:
                print(f"   ⚠️  Unexpected status: {join_response.status_code}")
                
        else:
            print("   ❌ Could not extract CSRF token")
    
    # Test 3: Test with wrong CSRF token
    print("\n3. Testing with invalid CSRF token...")
    
    invalid_response = client.post(
        f'/community/challenges/{challenge.id}/join/',
        data={'csrfmiddlewaretoken': 'invalid_token_12345'}
    )
    
    print(f"   Invalid CSRF POST Status: {invalid_response.status_code}")
    
    if invalid_response.status_code == 403:
        print("   ✅ Invalid CSRF token correctly rejected")
    else:
        print("   ⚠️  Invalid CSRF token not rejected as expected")
    
    print("\n" + "=" * 50)
    print("🎉 Challenge Join Test Complete!")

if __name__ == '__main__':
    test_challenge_join()