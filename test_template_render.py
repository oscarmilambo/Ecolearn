#!/usr/bin/env python
"""
Test template rendering directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from community.models import CommunityCampaign
from django.utils import timezone

print("="*60)
print("TESTING TEMPLATE RENDERING")
print("="*60)

# Get campaigns
upcoming_campaigns = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    start_date__gte=timezone.now()
).order_by('start_date')

ongoing_campaigns = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    start_date__lte=timezone.now(),
    end_date__gte=timezone.now()
).order_by('start_date')

past_campaigns = CommunityCampaign.objects.filter(
    is_active=True,
    is_published=True,
    end_date__lt=timezone.now()
).order_by('-start_date')[:5]

print(f"Upcoming: {upcoming_campaigns.count()}")
print(f"Ongoing: {ongoing_campaigns.count()}")
print(f"Past: {past_campaigns.count()}")

# Test context
context = {
    'upcoming_campaigns': upcoming_campaigns,
    'ongoing_campaigns': ongoing_campaigns,
    'past_campaigns': past_campaigns,
    'user_campaigns': [],
}

print(f"\nContext keys: {list(context.keys())}")

# Try to render template
try:
    print("\n1. Testing template rendering...")
    rendered = render_to_string('community/campaigns_list.html', context)
    print(f"   Rendered length: {len(rendered)} characters")
    
    if len(rendered) > 0:
        print("   ✅ Template rendered successfully!")
        print(f"   Preview: {rendered[:200]}...")
        
        # Check for key elements
        if '<html' in rendered.lower():
            print("   ✅ Contains HTML")
        if 'campaigns' in rendered.lower():
            print("   ✅ Contains 'campaigns'")
        if 'community' in rendered.lower():
            print("   ✅ Contains 'community'")
            
    else:
        print("   ❌ Template rendered but is empty!")
        
except Exception as e:
    print(f"   ❌ Template rendering error: {e}")
    import traceback
    traceback.print_exc()

# Test with minimal context
print("\n2. Testing with minimal context...")
try:
    minimal_context = {
        'upcoming_campaigns': [],
        'ongoing_campaigns': [],
        'past_campaigns': [],
        'user_campaigns': [],
    }
    
    rendered = render_to_string('community/campaigns_list.html', minimal_context)
    print(f"   Minimal render length: {len(rendered)} characters")
    
    if len(rendered) > 0:
        print("   ✅ Minimal template works!")
    else:
        print("   ❌ Even minimal template is empty!")
        
except Exception as e:
    print(f"   ❌ Minimal template error: {e}")

# Test base template
print("\n3. Testing base template...")
try:
    base_rendered = render_to_string('base.html', {})
    print(f"   Base template length: {len(base_rendered)} characters")
    
    if len(base_rendered) > 0:
        print("   ✅ Base template works!")
    else:
        print("   ❌ Base template is empty!")
        
except Exception as e:
    print(f"   ❌ Base template error: {e}")

# Test simple template
print("\n4. Creating and testing simple template...")
simple_template_content = """
{% extends 'base.html' %}

{% block title %}Test Campaigns{% endblock %}

{% block content %}
<div class="container">
    <h1>Test Campaigns Page</h1>
    
    <p>Upcoming: {{ upcoming_campaigns|length }}</p>
    <p>Ongoing: {{ ongoing_campaigns|length }}</p>
    <p>Past: {{ past_campaigns|length }}</p>
    
    {% if upcoming_campaigns %}
        <h2>Upcoming Campaigns</h2>
        {% for campaign in upcoming_campaigns %}
            <div>{{ campaign.title }} - {{ campaign.location }}</div>
        {% endfor %}
    {% else %}
        <p>No upcoming campaigns</p>
    {% endif %}
    
    {% if ongoing_campaigns %}
        <h2>Ongoing Campaigns</h2>
        {% for campaign in ongoing_campaigns %}
            <div>{{ campaign.title }} - {{ campaign.location }}</div>
        {% endfor %}
    {% else %}
        <p>No ongoing campaigns</p>
    {% endif %}
    
    {% if past_campaigns %}
        <h2>Past Campaigns</h2>
        {% for campaign in past_campaigns %}
            <div>{{ campaign.title }} - {{ campaign.location }}</div>
        {% endfor %}
    {% else %}
        <p>No past campaigns</p>
    {% endif %}
</div>
{% endblock %}
"""

# Write simple template
with open('community/templates/community/campaigns_list_simple.html', 'w', encoding='utf-8') as f:
    f.write(simple_template_content)

try:
    simple_rendered = render_to_string('community/campaigns_list_simple.html', context)
    print(f"   Simple template length: {len(simple_rendered)} characters")
    
    if len(simple_rendered) > 0:
        print("   ✅ Simple template works!")
        print(f"   Preview: {simple_rendered[:300]}...")
    else:
        print("   ❌ Simple template is empty!")
        
except Exception as e:
    print(f"   ❌ Simple template error: {e}")

print("\n" + "="*60)