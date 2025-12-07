"""
Management command to fix points for already approved challenge proofs
Run this to retroactively award points for existing approved proofs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from community.models import ChallengeProof
from gamification.models import UserPoints
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Fix points for already approved challenge proofs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting points fix for approved challenge proofs...'))
        
        # Get all approved proofs
        approved_proofs = ChallengeProof.objects.filter(status='approved')
        total_proofs = approved_proofs.count()
        
        if total_proofs == 0:
            self.stdout.write(self.style.SUCCESS('No approved proofs found. Nothing to fix.'))
            return
        
        self.stdout.write(f'Found {total_proofs} approved proofs to process...')
        
        fixed_count = 0
        skipped_count = 0
        
        for proof in approved_proofs:
            # Calculate points
            points = proof.bags_collected * 30
            
            # Check if points were already awarded
            if proof.points_awarded == points:
                # Points already set correctly, but let's verify user has them
                user = proof.participant.user
                
                # Update gamification points
                try:
                    user_points, created = UserPoints.objects.get_or_create(user=user)
                    # Check if this proof was already counted
                    from gamification.models import PointTransaction
                    existing_transaction = PointTransaction.objects.filter(
                        user=user,
                        reference_id=proof.id,
                        transaction_type='challenge_complete'
                    ).exists()
                    
                    if not existing_transaction:
                        user_points.add_points(
                            points, 
                            'challenge_complete', 
                            f'Challenge proof approved: {proof.bags_collected} bags (retroactive)',
                            reference_id=proof.id
                        )
                        self.stdout.write(f'  ✓ Added {points} points to gamification for {user.username}')
                    else:
                        self.stdout.write(f'  - Gamification points already exist for proof #{proof.id}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Gamification error for {user.username}: {e}'))
                
                # Update user profile points
                try:
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    # We'll add the points anyway since we can't easily track if they were added before
                    profile.points += points
                    profile.save()
                    self.stdout.write(f'  ✓ Added {points} points to profile for {user.username}')
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Profile error for {user.username}: {e}'))
                    skipped_count += 1
            else:
                # Points not set, update everything
                proof.points_awarded = points
                proof.save()
                
                user = proof.participant.user
                
                # Update gamification points
                try:
                    user_points, created = UserPoints.objects.get_or_create(user=user)
                    user_points.add_points(
                        points, 
                        'challenge_complete', 
                        f'Challenge proof approved: {proof.bags_collected} bags (retroactive)',
                        reference_id=proof.id
                    )
                    self.stdout.write(f'  ✓ Added {points} points to gamification for {user.username}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Gamification error for {user.username}: {e}'))
                
                # Update user profile points
                try:
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.points += points
                    profile.save()
                    self.stdout.write(f'  ✓ Added {points} points to profile for {user.username}')
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Profile error for {user.username}: {e}'))
                    skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Points fix complete!'))
        self.stdout.write(f'  - Fixed: {fixed_count} proofs')
        self.stdout.write(f'  - Skipped: {skipped_count} proofs')
        self.stdout.write(f'  - Total processed: {total_proofs} proofs')
