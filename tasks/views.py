from django.shortcuts import render
from .models import Task, Task_Checkup


def user_task_overview(request):
    """Render a user's task overview page."""
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/task_overview.html', context)
