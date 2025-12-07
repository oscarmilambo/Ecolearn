#!/usr/bin/env python
"""
Script to improve category icons and colors for better visual display
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from elearning.models import Category

def improve_category_display():
    print("🎨 Improving Category Display")
    print("=" * 50)
    
    # Define better icons and colors for categories
    category_improvements = {
        'Waste Management Basics': {
            'icon_class': 'fas fa-trash-alt',
            'color': '#10B981'  # Green
        },
        'Waste Segregation': {
            'icon_class': 'fas fa-sort-amount-up',
            'color': '#3B82F6'  # Blue
        },
        'Recycling Techniques': {
            'icon_class': 'fas fa-recycle',
            'color': '#059669'  # Emerald
        },
        'Recycling': {
            'icon_class': 'fas fa-recycle',
            'color': '#059669'  # Emerald
        },
        'Home Composting': {
            'icon_class': 'fas fa-seedling',
            'color': '#65A30D'  # Lime
        },
        'Composting': {
            'icon_class': 'fas fa-seedling',
            'color': '#65A30D'  # Lime
        },
        'Electronic Waste': {
            'icon_class': 'fas fa-microchip',
            'color': '#7C3AED'  # Violet
        },
        'Circular Economy': {
            'icon_class': 'fas fa-sync-alt',
            'color': '#DC2626'  # Red
        },
        'Community Leadership': {
            'icon_class': 'fas fa-users',
            'color': '#EA580C'  # Orange
        },
        'E-Waste Management': {
            'icon_class': 'fas fa-laptop',
            'color': '#7C3AED'  # Violet
        },
        'Hazardous Waste': {
            'icon_class': 'fas fa-exclamation-triangle',
            'color': '#DC2626'  # Red
        }
    }
    
    updated_count = 0
    
    for category in Category.objects.all():
        if category.name in category_improvements:
            improvements = category_improvements[category.name]
            
            # Update icon and color
            old_icon = category.icon_class
            old_color = category.color
            
            category.icon_class = improvements['icon_class']
            category.color = improvements['color']
            category.save()
            
            print(f"✅ Updated {category.name}:")
            print(f"   Icon: {old_icon} → {category.icon_class}")
            print(f"   Color: {old_color} → {category.color}")
            
            updated_count += 1
        else:
            print(f"⚠️  No improvements defined for: {category.name}")
    
    print(f"\n🎉 Updated {updated_count} categories with better icons and colors!")
    print("\n📋 Category Display Summary:")
    
    for category in Category.objects.all():
        module_count = category.modules.count()
        published_count = category.modules.filter(is_published=True).count()
        print(f"   {category.icon_class} {category.name}: {published_count}/{module_count} modules")

if __name__ == "__main__":
    improve_category_display()