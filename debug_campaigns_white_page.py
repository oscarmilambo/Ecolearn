#!/usr/bin/env python
"""
Debug white page issue for campaigns
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from community.models import CommunityCampaign
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.conf import settings

print("="*80)
print("DEBUGGING CAMPAIGNS WHITE PAGE ISSUE")
print("="*80)

# 1. Check template exists
print("\n1. CHECKING TEMPLATE...")
template_paths = [
    'community/campaigns_list.html',
    'community/templates/community/campaigns_list.html',
    'templates/community/campaigns_list.html'
]

for path in template_paths:
    if os.path.exists(path):
        print(f"   ✅ Found template: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   Template size: {len(content)} characters")
            if '{% extends' in content:
                print(f"   ✅ Template extends base")
            if '{% for campaign in' in content:
                print(f"   ✅ Template has campaign loop")
            if '{% empty %}' in content or '{% else %}' in content:
                print(f"   ✅ Template has fallback for empty campaigns")
            else:
                print(f"   ⚠️  Template missing empty/else clause")
    else:
        print(f"   ❌ Not found: {path}")

# 2. Test template loading
print("\n2. TESTING TEMPLATE LOADING...")
try:
    template = get_template('community/campaigns_list.html')
    print(f"   ✅ Template loads successfully: {template.origin.name}")
except TemplateDoesNotExist as e:
    print(f"   ❌ Template not found: {e}")
    print(f"   Template dirs: {settings.TEMPLATES[0]['DIRS']}")

# 3. Check database
print("\n3. CHECKING DATABASE...")
campaigns = CommunityCampaign.objects.all()
print(f"   Total campaigns: {campaigns.count()}")

if campaigns.exists():
    for i, campaign in enumerate(campaigns[:3], 1):
        print(f"   {i}. {campaign.title}")
        print(f"      Active: {campaign.is_active}")
        print(f"      Published: {campaign.is_published}")
        print(f"      Start: {campaign.start_date}")

# 4. Test view directly
print("\n4. TESTING VIEW FUNCTION...")
try:
    from community.views import campaigns_list
    from django.http import HttpRequest
    from django.contrib.auth.models import AnonymousUser
    
    # Create mock request
    request = HttpRequest()
    request.method = 'GET'
    request.user = AnonymousUser()
    
    print("   ⚠️  Testing with anonymous user (should redirect to login)")
    
except Exception as e:
    print(f"   ❌ Error testing view: {e}")

# 5. Test with authenticated user
print("\n5. TESTING WITH AUTHENTICATED USER...")
User = get_user_model()

# Get or create test user
user, created = User.objects.get_or_create(
    username='debuguser',
    defaults={
        'email': 'debug@example.com',
        'first_name': 'Debug',
        'last_name': 'User'
    }
)
if created:
    user.set_password('debugpass123')
    user.save()

# Test with client
client = Client()
client.force_login(user)

print(f"   Testing as user: {user.username}")

# Test the actual URL
response = client.get('/community/campaigns/', HTTP_HOST='localhost')
print(f"   Status code: {response.status_code}")
print(f"   Content type: {response.get('Content-Type', 'N/A')}")
print(f"   Content length: {len(response.content)} bytes")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    print(f"   Response preview (first 200 chars):")
    print(f"   '{content[:200]}...'")
    
    # Check for common issues
    if len(content.strip()) == 0:
        print("   ❌ EMPTY RESPONSE - This is the white page issue!")
    elif '<html' not in content.lower():
        print("   ❌ No HTML tags found")
    elif 'campaigns' in content.lower():
        print("   ✅ Content contains 'campaigns'")
    else:
        print("   ⚠️  Content doesn't contain 'campaigns'")
        
    # Check for template errors
    if 'TemplateSyntaxError' in content:
        print("   ❌ Template syntax error found")
    if 'TemplateDoesNotExist' in content:
        print("   ❌ Template does not exist error")
        
else:
    print(f"   ❌ HTTP Error: {response.status_code}")
    if hasattr(response, 'content'):
        print(f"   Error content: {response.content.decode('utf-8')[:500]}")

# 6. Check context data
print("\n6. CHECKING CONTEXT DATA...")
if response.status_code == 200 and hasattr(response, 'context'):
    context = response.context
    if context:
        print(f"   Context keys: {list(context.keys())}")
        for key in ['upcoming_campaigns', 'ongoing_campaigns', 'past_campaigns', 'user_campaigns']:
            if key in context:
                value = context[key]
                if hasattr(value, '__len__'):
                    print(f"   {key}: {len(value)} items")
                else:
                    print(f"   {key}: {value}")
    else:
        print("   ❌ No context data")

# 7. Test simple queryset
print("\n7. TESTING SIMPLE QUERYSET...")
try:
    all_campaigns = CommunityCampaign.objects.all()
    print(f"   All campaigns count: {all_campaigns.count()}")
    
    active_published = CommunityCampaign.objects.filter(is_active=True, is_published=True)
    print(f"   Active & published: {active_published.count()}")
    
    if active_published.exists():
        print("   ✅ Campaigns exist and should display")
    else:
        print("   ⚠️  No active published campaigns")
        
except Exception as e:
    print(f"   ❌ Database error: {e}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)