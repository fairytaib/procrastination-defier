from django import forms
from .models import Order
from django.core.exceptions import ValidationError


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['user', 'order_item']
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'street_address', 'apartment', 'city', 'postal_code', 'country',
            'is_default'
        ]

    widgets = {
        'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
        'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
        'street_address': forms.TextInput(
            attrs={'placeholder': 'Street Address'}),
        'apartment': forms.TextInput(attrs={'placeholder': 'Apartment'}),
        'city': forms.TextInput(attrs={'placeholder': 'City'}),
        'postal_code': forms.TextInput(attrs={'placeholder': 'Postal Code'}),
        'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        'is_default': forms.CheckboxInput()
    }

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code.isdigit():
            raise ValidationError("Postal code must be numeric.")
        return postal_code
