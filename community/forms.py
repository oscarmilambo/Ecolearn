from django import forms
from .models import (
    ForumTopic,
    ForumReply,
    CommunityEvent,
    SuccessStory,
    CommunityChallenge,
    HealthAlert
)

# Base styling (reuse everywhere)
BASE_INPUT = "w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200"
TEXTAREA = "w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-vertical transition-all duration-200"
FILE_INPUT = "block w-full text-sm text-gray-600 file:mr-4 file:py-2.5 file:px-5 file:rounded-full file:border-0 file:text-sm file:font-medium file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer"


class TopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': BASE_INPUT,
                'placeholder': 'Enter a clear, descriptive topic title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 10,
                'placeholder': 'Share your question, idea, or experience in detail...',
                'required': True
            })
        }
        labels = {
            'title': 'Topic Title',
            'content': 'Content',
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 5,
                'placeholder': 'Write your helpful reply here...',
                'required': True
            })
        }
        labels = {
            'content': 'Your Reply',
        }


class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ['title', 'story_type', 'content', 'location', 'image', 'video_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': BASE_INPUT,
                'placeholder': 'e.g. "We cleaned 500kg of plastic from Lusaka!"',
            }),
            'story_type': forms.Select(attrs={'class': BASE_INPUT}),
            'content': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 12,
                'placeholder': 'Tell your inspiring environmental success story... What did you do? How did it impact your community?'
            }),
            'location': forms.TextInput(attrs={
                'class': BASE_INPUT,
                'placeholder': 'e.g. Matero, Lusaka'
            }),
            'image': forms.FileInput(attrs={'class': FILE_INPUT}),
            'video_url': forms.URLInput(attrs={
                'class': BASE_INPUT,
                'placeholder': 'https://youtube.com/... (optional)'
            }),
        }
        labels = {
            'title': 'Story Title',
            'story_type': 'Category',
            'content': 'Your Story',
            'location': 'Location',
            'image': 'Photo (optional)',
            'video_url': 'Video Link (YouTube, etc.)',
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = CommunityEvent
        fields = [
            'title', 'title_bem', 'title_ny',
            'description', 'description_bem', 'description_ny',
            'event_type', 'location', 'latitude', 'longitude',
            'start_date', 'end_date', 'max_participants',
            'registration_deadline', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT, 'placeholder': 'Event title in English'}),
            'title_bem': forms.TextInput(attrs={'class': BASE_INPUT, 'placeholder': 'Title in Bemba (optional)'}),
            'title_ny': forms.TextInput(attrs={'class': BASE_INPUT, 'placeholder': 'Title in Nyanja (optional)'}),
            
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 6, 'placeholder': 'Full description in English'}),
            'description_bem': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 4, 'placeholder': 'Description in Bemba (optional)'}),
            'description_ny': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 4, 'placeholder': 'Description in Nyanja (optional)'}),
            
            'event_type': forms.Select(attrs={'class': BASE_INPUT}),
            'location': forms.TextInput(attrs={'class': BASE_INPUT, 'placeholder': 'e.g. Independence Stadium, Lusaka'}),
            'latitude': forms.NumberInput(attrs={'class': BASE_INPUT, 'step': 'any', 'placeholder': 'e.g. -15.3875'}),
            'longitude': forms.NumberInput(attrs={'class': BASE_INPUT, 'step': 'any', 'placeholder': 'e.g. 28.3228'}),
            
            'start_date': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
            'max_participants': forms.NumberInput(attrs={'class': BASE_INPUT, 'min': 1, 'placeholder': 'Leave blank for unlimited'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
            'image': forms.FileInput(attrs={'class': FILE_INPUT}),
        }
        labels = {
            'title': 'Event Title (English)',
            'title_bem': 'Title (Bemba)',
            'title_ny': 'Title (Nyanja)',
            'description': 'Description (English)',
            'description_bem': 'Description (Bemba)',
            'description_ny': 'Description (Nyanja)',
            'max_participants': 'Maximum Participants',
            'registration_deadline': 'Registration Deadline',
        }


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = CommunityChallenge
        fields = ['title', 'description', 'challenge_type', 'start_date', 'end_date', 'target_goal', 'reward_points', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT, 'placeholder': 'e.g. Collect 1000kg of plastic'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 6}),
            'challenge_type': forms.Select(attrs={'class': BASE_INPUT}),
            'start_date': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
            'target_goal': forms.NumberInput(attrs={'class': BASE_INPUT, 'min': 1}),
            'reward_points': forms.NumberInput(attrs={'class': BASE_INPUT, 'min': 0, 'value': 150}),
            'image': forms.FileInput(attrs={'class': FILE_INPUT}),
        }


class HealthAlertForm(forms.ModelForm):
    class Meta:
        model = HealthAlert
        fields = [
            'alert_type', 'severity', 'title', 'message', 'location',
            'latitude', 'longitude', 'affected_areas', 'hygiene_tips', 'nearest_clinics', 'expires_at'
        ]
        widgets = {
            'alert_type': forms.Select(attrs={'class': BASE_INPUT}),
            'severity': forms.Select(attrs={'class': BASE_INPUT}),
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'message': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 5}),
            'location': forms.TextInput(attrs={'class': BASE_INPUT}),
            'latitude': forms.NumberInput(attrs={'class': BASE_INPUT, 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': BASE_INPUT, 'step': 'any'}),
            'affected_areas': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 3, 'placeholder': 'Kanyama, Matero, Chawama...'}),
            'hygiene_tips': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 5}),
            'nearest_clinics': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 5}),
            'expires_at': forms.DateTimeInput(attrs={'class': BASE_INPUT, 'type': 'datetime-local'}),
        }