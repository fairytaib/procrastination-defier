from django.apps import apps


def get_current_subscription(user):
    Subscription = apps.get_model('subscription', 'Subscription')
    return (Subscription.objects
            .filter(user=user)
            .order_by('-start_date')
            .first())


def open_tasks_count(user):
    Task = apps.get_model('tasks', 'Task')
    return Task.objects.filter(user=user, completed=False).count()


def can_add_task(user):
    sub = get_current_subscription(user)
    if not sub:
        return False
    if sub.tasks_quota == 0:
        return True
    return open_tasks_count(user) < sub.tasks_quota
