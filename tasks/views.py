from django.shortcuts import render, get_object_or_404
from .models import Task, Task_Checkup
from django.contrib.auth.decorators import login_required


@login_required
def user_task_overview(request):
    """Render a user's task overview page."""
    tasks = Task.objects.filter(
        user=request.user, completed=False).order_by('-created_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/user_task_overview.html', context)


def view_task_details(request, task_id):
    """Display the details of a task."""
    task = get_object_or_404(Task, id=task_id)
    task_checkup = Task_Checkup.objects.filter(task=task).first()

    context = {
        "task": task,
        "task_id": task_id,
        "task_checkup": task_checkup,
    }

    return render(request, "tasks/view_task_details.html", context)
