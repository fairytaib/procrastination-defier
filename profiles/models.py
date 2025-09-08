from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class UserProfile(models.Model):
    """Model to store user profile information including profile picture."""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    profile_picture = CloudinaryField(
        'image', blank=True, null=True,
        help_text="Upload a profile picture.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
