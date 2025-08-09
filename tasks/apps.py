from django.apps import AppConfig



class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        import tasks.signals
        from .models import Task
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(Task)
        permission, created = Permission.objects.get_or_create(
            codename="mark_done",
            name="Mark Task as done",
            content_type=content_type,
        )