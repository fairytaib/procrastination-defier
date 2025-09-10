from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _



class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    interval = models.CharField(max_length=5, default='month')
    tasks_quota = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    cancel_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return not self.end_date or now() < self.end_date

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
