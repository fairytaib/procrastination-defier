from django.db.models.signals import post_save
from django.dispatch import receiver
from checkout.models import Order
from rewards.models import RewardHistory


@receiver(post_save, sender=Order)
def create_reward_history(sender, instance, created, **kwargs):
    if created:
        # Create a RewardHistory entry for the new order
        RewardHistory.objects.create(
            user=instance.user,
            reward=instance.reward
        )
