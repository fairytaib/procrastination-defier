from django.db import models
from cloudinary.models import CloudinaryField
from multiselectfield import MultiSelectField
import pycountry

from django.contrib.auth.models import User

REWARD_TYPES = [
    ('digital', 'Digital'),
    ('discount', 'Discount Code'),
    ('travel', 'Travel'),
    ('wellness', 'Wellness'),
    ('food', 'Food'),
    ('entertainment', 'Entertainment'),
    ('other', 'Other'),
]

COUNTRY_CHOICES = [
    (country.alpha_2, country.name) for country in pycountry.countries
]


class Reward(models.Model):
    """A reward model to represent the rewards in the system."""

    name = models.CharField(max_length=100, unique=True)
    image = CloudinaryField(
        'image', default='placeholder',
        blank=True, null=True)
    description = models.TextField()
    cost = models.PositiveIntegerField(
        help_text="Cost in points to redeem this reward.", default=1000)
    stock = models.PositiveIntegerField(
        help_text="Number of items available for this reward.", default=0)
    reward_type = models.CharField(
        choices=REWARD_TYPES,
        max_length=50,
        verbose_name="Reward Type",
    )
    available_countries = MultiSelectField(
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Reward available in Countries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RewardHistory(models.Model):
    """A model to track the history of rewards bought by users."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='reward_history')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE,
                               related_name='reward_history')
    bought_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{
            self.user.username
            } bought {self.reward.name} on {self.bought_at}"
