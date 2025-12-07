"""
Context processors for admin dashboard
Makes certain variables available in all templates
"""

def pending_proofs_count(request):
    """Add pending challenge proofs count to all admin dashboard templates"""
    if request.user.is_authenticated and request.user.is_staff:
        from community.models import ChallengeProof
        count = ChallengeProof.objects.filter(status='pending').count()
        return {'pending_proofs_count': count}
    return {'pending_proofs_count': 0}
