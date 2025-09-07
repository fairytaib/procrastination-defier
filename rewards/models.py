from django.db import models
from cloudinary.models import CloudinaryField
from multiselectfield import MultiSelectField

from django.contrib.auth.models import User

REWARD_TYPES = [
    ('digital', 'Digital'),
    ('discount', 'Discount Code'),
    ('travel', 'Travel'),
    ('wellness', 'Wellness'),
    ('food', 'Food'),
    ('fashion', 'Fashion'),
    ('electronics', 'Electronics'),
    ('entertainment', 'Entertainment'),
    ('other', 'Other'),
]

# COUNTRY_CHOICES = [
#     (country.alpha_2, country.name) for country in pycountry.countries
# ]

COUNTRY_CHOICES = [
    # ('US', 'United States'),
    # ('CA', 'Canada'),
    # ('GB', 'United Kingdom'),
    # ('AU', 'Australia'),
    # ('IN', 'India'),
    # ('JP', 'Japan'),
    # ('CN', 'China'),
    # ('BR', 'Brazil'),
    # Only European countries for the time being
    ('Everywhere', 'Everywhere'),
    ('FR', 'France'),
    ('DE', 'Germany'),
    ('ES', 'Spain'),
    ('IT', 'Italy'),
    ('NL', 'Netherlands'),
    ('SE', 'Sweden'),
    ('NO', 'Norway'),
    ('FI', 'Finland'),
    ('DK', 'Denmark'),
    ('BE', 'Belgium'),
    ('CH', 'Switzerland'),
    ('AT', 'Austria'),
    ('IE', 'Ireland'),
    ('PT', 'Portugal'),
    ('GR', 'Greece'),
    ('PL', 'Poland'),
    ('CZ', 'Czech Republic'),
    ('HU', 'Hungary'),
    ('RO', 'Romania'),
    ('BG', 'Bulgaria'),
    ('HR', 'Croatia'),
    ('SI', 'Slovenia'),
    ('SK', 'Slovakia'),
]


class Reward(models.Model):
    """A reward model to represent the rewards in the system."""

    name = models.CharField(max_length=100, unique=True,
                            null=False, blank=False)
    image = CloudinaryField(
        'image', default='placeholder',
        blank=True, null=True)
    description = models.TextField(max_length=1000, null=False, blank=False)
    cost = models.PositiveIntegerField(
        help_text="Cost in points to redeem this reward.",
        default=1000, blank=False, null=False)
    stock = models.PositiveIntegerField(
        help_text="Number of items available for this reward.",
        default=10, blank=False, null=False)
    reward_type = models.CharField(
        choices=REWARD_TYPES,
        max_length=50,
        verbose_name="Reward Type",
        null=False, blank=False
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
    reward_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{
            self.user.username
            } bought {self.reward.name} on {self.bought_at}"
