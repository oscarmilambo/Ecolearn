"""
Test script to verify the challenge points system is working correctly
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from community.models import ChallengeProof, ChallengeParticipant
from gamification.models import UserPoints
from accounts.models import UserProfile

print("=" * 60)
print("CHALLENGE POINTS SYSTEM TEST")
print("=" * 60)

# Check approved proofs
approved_proofs = ChallengeProof.objects.filter(status='approved')
print(f"\n✓ Approved proofs: {approved_proofs.count()}")

if approved_proofs.exists():
    for proof in approved_proofs:
        user = proof.participant.user
        bags = proof.bags_collected
        points_awarded = proof.points_awarded
        expected_points = bags * 30
        
        print(f"\n  Proof #{proof.id}:")
        print(f"    User: {user.username}")
        print(f"    Bags: {bags}")
        print(f"    Points awarded: {points_awarded}")
        print(f"    Expected: {expected_points}")
        print(f"    ✓ Correct!" if points_awarded == expected_points else "    ✗ MISMATCH!")
        
        # Check participant contribution
        participant = proof.participant
        print(f"    Participant contribution: {participant.contribution} bags")
        
        # Check gamification points
        try:
            user_points = UserPoints.objects.get(user=user)
            print(f"    Gamification total: {user_points.total_points} pts")
            print(f"    Gamification available: {user_points.available_points} pts")
        except UserPoints.DoesNotExist:
            print(f"    ✗ No gamification points record!")
        
        # Check user profile points
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"    Profile points: {profile.points} pts")
        except UserProfile.DoesNotExist:
            print(f"    ✗ No user profile!")

# Check pending proofs
pending_proofs = ChallengeProof.objects.filter(status='pending')
print(f"\n✓ Pending proofs: {pending_proofs.count()}")

if pending_proofs.exists():
    print("\n  Pending proofs waiting for approval:")
    for proof in pending_proofs:
        user = proof.participant.user
        bags = proof.bags_collected
        potential_points = bags * 30
        print(f"    - {user.username}: {bags} bags → {potential_points} pts (when approved)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. If you have pending proofs, approve them in admin")
print("2. Check that points are awarded automatically")
print("3. Verify leaderboard updates instantly")
print("4. Check user profile shows correct total points")
