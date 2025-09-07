from django import forms
from .models import Reward
from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
import re


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = [
            'name', 'image',
            'description', 'cost',
            'stock', 'reward_type',
            'available_countries'
            ]
        labels = {
            'name': 'Reward Name',
            'image': 'Reward Image',
            'description': 'Reward Description',
            'cost': 'Cost (in points)',
            'stock': 'Stock Quantity',
            'reward_type': 'Reward Type',
            'available_countries': 'Available Countries'
        }

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Reward Name'}
                ),
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                       'placeholder': 'Describe the reward as detailed as possible',
                       'rows': 3
                       }
                ),
            'cost': forms.NumberInput(
                attrs={
                    'class': 'form-control', 'placeholder': 'Cost in points'
                    }
            ),
            'stock': forms.NumberInput(
                attrs={
                    'class': 'form-control', 'placeholder': 'Stock Quantity'
                    }
            ),
            'reward_type': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'available_countries': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }

    def clean_name(self):
        """Ensure name contains only letters, numbers, and spaces."""
        name = self.cleaned_data.get('name')
        if not re.match(r'^[A-Za-z0-9\s]+$', name):
            raise ValidationError(
                "Name can only contain letters, numbers, and spaces.")
        return name

    def clean_description(self):
        """Ensure description is sufficiently detailed."""
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise ValidationError(
                "Description must be at least 10 characters long.")
        return description

    def clean_cost(self):
        """Ensure cost is positive."""
        cost = self.cleaned_data.get('cost')
        if cost <= 0:
            raise ValidationError('Cost must be positive.')
        return cost

    def clean_stock(self):
        """Ensure stock is non-negative."""
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise ValidationError('Stock cannot be negative.')
        return stock

    def clean_image(self):
        """Validate uploaded image file type."""
        f = self.cleaned_data.get('image')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        try:
            with Image.open(f) as im:
                fmt = (im.format or '').lower()
            with Image.open(f) as im:
                im.verify()
        except (UnidentifiedImageError, Exception):
            raise ValidationError("Uploaded file is not a valid image.")

        if fmt not in {'jpeg', 'jpg', 'png', 'webp'}:
            raise ValidationError(
                "Only JPEG, JPG, PNG or WEBP images are allowed."
                )
        self._validate_size(f, 'image')
        return f
