from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserPoints, Task_Checkup


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.create(
            user=instance,
            points=0,
        )


@receiver(post_save, sender=UserPoints)
def connect_task_to_checkup(sender, instance, created, **kwargs):
    if created:
        Task_Checkup.objects.create(
            task=instance.task
        )
