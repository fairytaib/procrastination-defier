from django import forms
from .models import Order
from rewards.models import RewardHistory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class OrderForm(forms.ModelForm):
    """Form for creating and updating orders."""
    class Meta:
        model = Order
        exclude = ['user', 'order_item']
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'street_address', 'apartment', 'city', 'postal_code', 'country',
            'is_default'
        ]

        labels = {
                'is_default': 'Save for the future'
            }

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.TextInput(
                attrs={'placeholder': 'Phone Number'}
                ),
            'street_address': forms.TextInput(
                attrs={'placeholder': 'Street Address'}),
            'apartment': forms.TextInput(attrs={'placeholder': 'Apartment'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'postal_code': forms.TextInput(
                attrs={'placeholder': 'Postal Code'}
                ),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'is_default': forms.CheckboxInput()
        }

        def clean_postal_code(self):
            """Example of custom validation for postal code."""
            postal_code = self.cleaned_data.get('postal_code')
            if not postal_code.isdigit():
                raise ValidationError("Postal code must be numeric.")
            return postal_code


class RewardHistoryForm(forms.ModelForm):
    """Form for updating reward history."""
    class Meta:
        model = RewardHistory
        exclude = ['user', 'reward', 'bought_at']
        fields = ['reward_sent']

        widgets = {
            'reward_sent': forms.CheckboxInput(
                attrs={'class': 'form-check-input'})
        }

        labels = {
            'reward_sent': 'Reward Sent'
        }
