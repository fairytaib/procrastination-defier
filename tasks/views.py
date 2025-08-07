from django.shortcuts import render
from .models import Task, Task_Checkup
from django.contrib.auth.decorators import login_required


@login_required
def user_task_overview(request):
    """Render a user's task overview page."""
    tasks = Task.objects.filter(user=request.user, completed=False).order_by('-created_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/user_task_overview.html', context)
