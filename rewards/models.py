from django.db import models
from cloudinary.models import CloudinaryField
from multiselectfield import MultiSelectField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

REWARD_TYPES = [
    ('Digital', 'Digital'),
    ('Discount Code', 'Discount Code'),
    ('Travel', 'Travel'),
    ('Wellness', 'Wellness'),
    ('Food', 'Food'),
    ('Electronics', 'Electronics'),
    ('Entertainment', 'Entertainment'),
    ('Other', 'Other'),
]

COUNTRY_CHOICES = [
    # ('US', 'United States'),
    # ('CA', 'Canada'),
    # ('GB', 'United Kingdom'),
    # ('AU', 'Australia'),
    # ('IN', 'India'),
    # ('JP', 'Japan'),
    # ('CN', 'China'),
    # ('BR', 'Brazil'),
    # Only European countries for the time being. Will be implemented later
    ('Everywhere', 'Everywhere'),
    ('France', 'France'),
    ('Germany', 'Germany'),
    ('Spain', 'Spain'),
    ('Italy', 'Italy'),
    ('Netherlands', 'Netherlands'),
    ('Sweden', 'Sweden'),
    ('Norway', 'Norway'),
    ('Finland', 'Finland'),
    ('Denmark', 'Denmark'),
    ('Belgium', 'Belgium'),
    ('Switzerland', 'Switzerland'),
    ('Austria', 'Austria'),
    ('Ireland', 'Ireland'),
    ('Portugal', 'Portugal'),
    ('Greece', 'Greece'),
    ('Poland', 'Poland'),
    ('Czech Republic', 'Czech Republic'),
    ('Hungary', 'Hungary'),
    ('Romania', 'Romania'),
    ('Bulgaria', 'Bulgaria'),
    ('Croatia', 'Croatia'),
    ('Slovenia', 'Slovenia'),
    ('Slovakia', 'Slovakia'),
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
        help_text=_("Cost in points to redeem this reward."),
        default=1000, blank=False, null=False)
    stock = models.PositiveIntegerField(
        help_text=_("Number of items available for this reward."),
        default=10, blank=False, null=False)
    reward_type = models.CharField(
        choices=REWARD_TYPES,
        max_length=50,
        verbose_name="Reward Type",
        null=False, blank=False
    )
    available_countries = MultiSelectField(
        choices=COUNTRY_CHOICES,
        blank=False,
        null=False,
        default=['Everywhere'],
        verbose_name="Reward available in Countries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RewardHistory(models.Model):
    """A model to track the history of rewards bought by users."""
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reward_history'
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reward_history'
    )
    bought_at = models.DateTimeField(auto_now_add=True)
    reward_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{
            self.user.username
            } bought {self.reward.name} on {self.bought_at}"
