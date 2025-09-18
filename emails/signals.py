from django.db.models.signals import post_save
from django.dispatch import receiver
from rewards.models import RewardHistory
from checkout.models import Order
from .emails import send_reward_purchase_email


@receiver(post_save, sender=RewardHistory)
def reward_history_created(sender, instance, created, **kwargs):
    """Send an email when a RewardHistory instance is created."""
    if not created:
        return
    order = (
        Order.objects
        .filter(user=instance.user, order_item=instance.reward)
        .order_by("-id")
        .first()
    )
    if order:
        send_reward_purchase_email(
            order=order, reward=instance.reward, history=instance
            )
