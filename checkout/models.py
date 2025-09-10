from django.db import models
from django.contrib.auth.models import User
from rewards.models import Reward
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """Model to store order details including user information and address."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='addresses'
    )
    order_item = models.ForeignKey(
        Reward, on_delete=models.CASCADE, related_name='order_items'
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(blank=False)
    phone_number = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=255, blank=False)
    apartment = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=False)
    postal_code = models.CharField(max_length=20, blank=False)
    country = models.CharField(max_length=100, blank=False)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Address"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            )
        ]
