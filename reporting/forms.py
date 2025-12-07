from django import forms
from .models import DumpingReport, ReportUpdate


class DumpingReportForm(forms.ModelForm):
    class Meta:
        model = DumpingReport
        fields = [
            'is_anonymous', 'reporter_contact', 'location_description',
            'latitude', 'longitude', 'description', 'severity',
            'waste_type', 'estimated_volume', 'photo1', 'photo2', 'photo3'
        ]
        widgets = {
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50'
            }),
            'reporter_contact': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Optional contact for follow-up'
            }),
            'location_description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Describe the location (e.g., "Behind City Mall, near the river")'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'step': 'any',
                'readonly': True
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'step': 'any',
                'readonly': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'rows': 4,
                'placeholder': 'Describe what you observed (type of waste, amount, any hazards, etc.)'
            }),
            'severity': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
            'waste_type': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., plastic bottles, food waste, construction debris'
            }),
            'estimated_volume': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., small pile, 1-2 cubic meters, truck load'
            }),
            'photo1': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': 'image/*'
            }),
            'photo2': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': 'image/*'
            }),
            'photo3': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo1'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True


class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = ReportUpdate
        fields = ['update_text', 'is_public']
        widgets = {
            'update_text': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'rows': 4,
                'placeholder': 'Enter update details...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50'
            }),
        }


class TrackReportForm(forms.Form):
    reference_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Enter your reference number (e.g., ECO12345678)'
        })
    )
