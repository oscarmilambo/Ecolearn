from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, UserProfile

class CustomUserCreationForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
        })
    )
    
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('female', 'Female'),
        ('male', 'Male'),
        ('custom', 'Custom'),
    ]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition bg-white'
        })
    )
    
    # Mobile number or email field
    contact_method = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Mobile number or email',
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
        }),
        help_text='Enter your mobile number or email address'
    )
    
    # Single password field
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': 'w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
        }),
        help_text='Must be at least 8 characters'
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if CustomUser.objects.filter(email=email.lower()).exists():
                raise ValidationError("This email is already registered. Please use another or login.")
            return email.lower()
        return email

    def clean_contact_method(self):
        contact = self.cleaned_data.get('contact_method')
        
        # Check if it's an email
        if '@' in contact:
            # Validate email format
            try:
                from django.core.validators import validate_email
                validate_email(contact)
                # Check if email already exists
                if CustomUser.objects.filter(email=contact.lower()).exists():
                    raise ValidationError("This email is already registered. Please use another or login.")
                return contact.lower()
            except ValidationError:
                raise ValidationError("Please enter a valid email address.")
        else:
            # Validate phone number format (basic validation)
            import re
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, contact.replace(' ', '').replace('-', '')):
                raise ValidationError("Please enter a valid phone number.")
            
            # Check if phone already exists
            clean_phone = contact.replace(' ', '').replace('-', '')
            if CustomUser.objects.filter(phone_number=clean_phone).exists():
                raise ValidationError("This phone number is already registered. Please use another or login.")
            return clean_phone
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'preferred_language', 'profile_picture', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                field.widget.attrs.update({
                    'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
                })

class SMSVerificationForm(forms.Form):
    phone_number = forms.CharField(max_length=20)
    verification_code = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            })