from django.apps import apps
from datetime import date, timedelta


def refresh_overdue_flags(user):
    """Check for overdue tasks and mark them as fee_to_pay."""
    Task = apps.get_model('tasks', 'Task')
    Task.objects.filter(
        user=user,
        completed=False,
        fee_to_pay=False,
        checkup_date__lt=date.today()
    ).update(checkup_state=True)


def mark_for_checkup(user):
    """Mark tasks for checkup if they are due soon."""
    Task = apps.get_model('tasks', 'Task')
    Task.objects.filter(
        user=user,
        completed=False,
        checkup_state=False,
        checkup_date__lt=date.today() + timedelta(days=2)
    ).update(checkup_state=True)


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
    """Check if user can add a new task based
    on their subscription and fees to pay."""
    refresh_overdue_flags(user)
    Task = apps.get_model('tasks', 'Task')

    if Task.objects.filter(
            user=user, completed=False, fee_to_pay=True
            ).exists():
        return False

    sub = get_current_subscription(user)
    if not sub:
        return False

    if sub.tasks_quota == 0:
        return True

    open_count = Task.objects.filter(user=user, completed=False).count()

    return open_count < sub.tasks_quota
