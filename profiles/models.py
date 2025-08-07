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
    profile_picture = CloudinaryField(
        'image', blank=True, null=True,
        help_text="Upload a profile picture.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
