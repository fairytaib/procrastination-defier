# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.exclude(
                pk=self.instance.pk
                ).filter(email__iexact=email).exists():
            raise forms.ValidationError("This Email already exists")
        return email


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]
