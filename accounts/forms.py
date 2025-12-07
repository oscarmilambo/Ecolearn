from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False, help_text="Optional. Enter your phone number.")
    preferred_language = forms.ChoiceField(
        choices=CustomUser.LANGUAGE_CHOICES,
        initial='en',
        required=True,
        help_text="Select your preferred language for the platform"
    )
    location = forms.CharField(max_length=255, required=False, help_text="Optional. Your city or region.")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'preferred_language', 'location', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = []
        self.fields['username'].help_text = "Enter any username you'd like - no restrictions on characters"
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_number

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