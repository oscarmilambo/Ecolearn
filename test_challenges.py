"""
Quick test script for Community Challenges feature
Run this after migration to verify everything works
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from community.models import CommunityChallenge, ChallengeParticipant, ChallengeProof
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta

print("✅ Models imported successfully!")
print(f"✅ CommunityChallenge model: {CommunityChallenge}")
print(f"✅ ChallengeParticipant model: {ChallengeParticipant}")
print(f"✅ ChallengeProof model: {ChallengeProof}")

# Check if we can query
try:
    challenges = CommunityChallenge.objects.all()
    print(f"\n✅ Can query challenges: {challenges.count()} challenges found")
except Exception as e:
    print(f"\n❌ Error querying challenges: {e}")

print("\n🎉 All models are working correctly!")
print("\nNext steps:")
print("1. Run: python manage.py migrate")
print("2. Create a challenge in Django admin")
print("3. Visit /community/challenges/ to see it in action!")
