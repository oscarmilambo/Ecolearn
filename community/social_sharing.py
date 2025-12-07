# community/social_sharing.py
"""
Social Media Sharing Utilities
Handles WhatsApp, Facebook, Twitter, and LinkedIn sharing
"""

from django.conf import settings
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class SocialShareService:
    """
    Generate share URLs for different social media platforms
    """
    
    @staticmethod
    def generate_share_text(content_type, obj):
        """
        Generate formatted share text based on content type
        
        Args:
            content_type: 'story', 'event', 'challenge', etc.
            obj: The object to share
        
        Returns:
            dict: {title, description, url, hashtags, image_url}
        """
        base_url = getattr(settings, 'SITE_URL', 'https://ecolearn.zm')
        
        if content_type == 'story':
            return {
                'title': f"🌍 {obj.title}",
                'description': obj.content[:200] + '...' if len(obj.content) > 200 else obj.content,
                'url': f"{base_url}/community/stories/{obj.id}/",
                'hashtags': ['EcoLearn', 'EnvironmentalAction', 'Zambia', obj.story_type],
                'image_url': obj.image.url if obj.image else None,
                'impact': getattr(obj, 'impact_metric', '')
            }
        
        elif content_type == 'event':
            return {
                'title': f"📅 {obj.title}",
                'description': f"Join us for {obj.title} on {obj.start_date.strftime('%B %d, %Y')} at {obj.location}",
                'url': f"{base_url}/community/events/{obj.id}/",
                'hashtags': ['EcoLearn', 'CommunityEvent', 'Zambia'],
                'image_url': obj.image.url if obj.image else None
            }
        
        elif content_type == 'challenge':
            return {
                'title': f"🏆 {obj.title}",
                'description': f"Join me in the {obj.title} challenge! Goal: {obj.goal}",
                'url': f"{base_url}/community/challenges/{obj.id}/",
                'hashtags': ['EcoLearn', 'Challenge', 'Environmental'],
                'image_url': obj.image.url if obj.image else None
            }
        
        return {}
    
    @staticmethod
    def get_whatsapp_share_url(share_data):
        """
        Generate WhatsApp share URL
        
        Args:
            share_data: Dict from generate_share_text()
        
        Returns:
            str: WhatsApp share URL
        """
        # Format message
        message_parts = [
            share_data['title'],
            '',
            share_data['description'],
        ]
        
        if share_data.get('impact'):
            message_parts.append(f"\nImpact: {share_data['impact']}")
        
        message_parts.extend([
            '',
            f"Read more: {share_data['url']}",
            '',
            ' '.join(f"#{tag}" for tag in share_data['hashtags'])
        ])
        
        message = '\n'.join(message_parts)
        encoded_message = quote_plus(message)
        
        # WhatsApp Web URL
        return f"https://wa.me/?text={encoded_message}"
    
    @staticmethod
    def get_facebook_share_url(share_data):
        """
        Generate Facebook share URL
        
        Args:
            share_data: Dict from generate_share_text()
        
        Returns:
            str: Facebook share URL
        """
        encoded_url = quote_plus(share_data['url'])
        encoded_quote = quote_plus(f"{share_data['title']}\n\n{share_data['description']}")
        
        # Facebook Share Dialog
        return f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_quote}"
    
    @staticmethod
    def get_twitter_share_url(share_data):
        """
        Generate Twitter share URL
        
        Args:
            share_data: Dict from generate_share_text()
        
        Returns:
            str: Twitter share URL
        """
        # Twitter has 280 character limit
        text = f"{share_data['title']}\n\n{share_data['description'][:150]}"
        hashtags = ','.join(share_data['hashtags'][:3])  # Max 3 hashtags
        
        encoded_text = quote_plus(text)
        encoded_url = quote_plus(share_data['url'])
        
        return f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}&hashtags={hashtags}"
    
    @staticmethod
    def get_linkedin_share_url(share_data):
        """
        Generate LinkedIn share URL
        
        Args:
            share_data: Dict from generate_share_text()
        
        Returns:
            str: LinkedIn share URL
        """
        encoded_url = quote_plus(share_data['url'])
        
        return f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
    
    @staticmethod
    def get_email_share_url(share_data):
        """
        Generate mailto: URL for email sharing
        
        Args:
            share_data: Dict from generate_share_text()
        
        Returns:
            str: mailto: URL
        """
        subject = quote_plus(share_data['title'])
        body = quote_plus(f"{share_data['description']}\n\nRead more: {share_data['url']}")
        
        return f"mailto:?subject={subject}&body={body}"
    
    @staticmethod
    def get_all_share_urls(content_type, obj):
        """
        Get all share URLs for an object
        
        Args:
            content_type: Type of content
            obj: Object to share
        
        Returns:
            dict: All share URLs
        """
        share_data = SocialShareService.generate_share_text(content_type, obj)
        
        return {
            'whatsapp': SocialShareService.get_whatsapp_share_url(share_data),
            'facebook': SocialShareService.get_facebook_share_url(share_data),
            'twitter': SocialShareService.get_twitter_share_url(share_data),
            'linkedin': SocialShareService.get_linkedin_share_url(share_data),
            'email': SocialShareService.get_email_share_url(share_data),
            'share_data': share_data
        }


# Singleton instance
social_share_service = SocialShareService()


def get_share_urls(content_type, obj):
    """
    Helper function to get share URLs
    
    Usage:
        share_urls = get_share_urls('story', story_object)
        # Returns: {whatsapp: url, facebook: url, ...}
    """
    return social_share_service.get_all_share_urls(content_type, obj)
