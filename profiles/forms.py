# forms.py
from django import forms
from django.contrib.auth.models import User


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.exclude(
                pk=self.instance.pk
                ).filter(email__iexact=email).exists():
            raise forms.ValidationError("Diese E-Mail wird bereits verwendet.")
        return email
