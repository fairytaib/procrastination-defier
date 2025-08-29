from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from rewards.models import Reward


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='addresses'
    )
    order_item = models.ForeignKey(
        Reward, on_delete=models.CASCADE, related_name='order_items'
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            )
        ]


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "active"),
        ("trialing", "trialing"),
        ("past_due", "past_due"),
        ("canceled", "canceled"),
        ("incomplete", "incomplete"),
        ("incomplete_expired", "incomplete_expired"),
        ("unpaid", "unpaid"),
        ("paused", "paused"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="subscription"
    )
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_price_id = models.CharField(max_length=255)
    plan_code = models.CharField(max_length=50)  # "standard" | "premium"
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()

    def monthly_limit(self) -> int:
        from django.conf import settings
        return settings.STRIPE_PLANS[self.stripe_price_id]["limit"]

    def is_active(self) -> bool:
        return self.status in {"active", "trialing"}
