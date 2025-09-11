# forms.py
from PIL import Image
from PIL import UnidentifiedImageError
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.translation import gettext_lazy as _


class AccountForm(forms.ModelForm):
    """Form for updating user account information."""
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.exclude(
                pk=self.instance.pk
                ).filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This Email already exists"))
        return email


class ProfilePictureForm(forms.ModelForm):
    """Form for uploading and validating profile pictures."""
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]

    labels = {
                'profile_picture': _('Profile Picture (JPEG, PNG, JPG or WEBP)'),
    }

    widgets = {
            'profile_picture': forms.FileInput(
                attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form and set CSS classes for fields."""
        super().__init__(*args, **kwargs)
        self.fields[
            'profile_picture'
        ].widget.attrs['class'] = 'form-control-file'

    def clean_image(self):
        """Validate the uploaded image file."""
        f = self.cleaned_data.get('profile_picture')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        try:
            with Image.open(f) as im:
                fmt = (im.format or '').lower()
            with Image.open(f) as im:
                im.verify()
        except (UnidentifiedImageError, Exception):
            raise forms.ValidationError(
                _("Uploaded file is not a valid image.")
            )

        if fmt not in {'jpeg', 'jpg', 'png', 'webp'}:
            raise forms.ValidationError(
                _("Only JPEG, JPG, PNG or WEBP images are allowed.")
            )
        return f
