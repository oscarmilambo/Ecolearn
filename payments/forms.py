from django import forms
from .models import PaymentProvider


class PaymentForm(forms.Form):
    PROVIDER_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
        ('zamtel', 'Zamtel Kwacha'),
    ]

    provider = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'focus:ring-green-500 h-4 w-4 text-green-600 border-gray-300'
        })
    )
    
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Enter your mobile number (e.g., 260971234567)'
        })
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        
        # Remove any spaces or special characters
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present
        if not phone_number.startswith('260'):
            if phone_number.startswith('0'):
                phone_number = '260' + phone_number[1:]
            else:
                phone_number = '260' + phone_number
        
        # Validate Zambian phone number format
        if not phone_number.startswith('260') or len(phone_number) != 12:
            raise forms.ValidationError('Please enter a valid Zambian phone number.')
        
        return phone_number
