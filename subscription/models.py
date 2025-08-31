from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    price = models.IntegerField()
    interval = models.CharField(max_length=50, default='month')
    tasks_quota = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    cancel_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        if self.end_date:
            if now() < self.end_date:
                return True
            else:
                return False
        else:
            return False

    @property
    def tier(self):
        tier_mapping = {
            "standard": 1,
            "premium": 2
        }
        tier = tier_mapping.get(self.product_name, None)
        return tier

    def __str__(self):
        return f"{self.user} - {self.product_name} - Active: {self.is_active}."
