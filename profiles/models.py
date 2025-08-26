from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    user_username = models.CharField(
        max_length=150, unique=True, blank=True, null=True)
    user_first_name = models.CharField(
        max_length=30, blank=True, null=True)
    user_last_name = models.CharField(
        max_length=30, blank=True, null=True)
    user_email = models.EmailField()
    user_password = models.CharField(
        max_length=128
    )
    profile_picture = CloudinaryField(
        'image', blank=True, null=True,
        help_text="Upload a profile picture.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='addresses'
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Address"
