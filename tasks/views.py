from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Task, Task_Checkup
from .forms import TaskForm


@login_required
def user_task_overview(request):
    """Render a user's task overview page."""
    admin = request.user.has_perm('tasks.mark_done')
    if not admin:
        tasks_undone = Task.objects.filter(
            user=request.user, completed=False).order_by('-created_at')
        task_done = Task.objects.filter(
            user=request.user, completed=True).order_by('created_at')
        context = {
            'tasks_undone': tasks_undone,
            'tasks_done': task_done,
        }
    else:
        tasks_undone = Task.objects.all().order_by(
            '-user', '-created_at'
            ).filter(completed=False)
        context = {
            'tasks_undone': tasks_undone,
        }
    return render(request, 'tasks/user_task_overview.html', context)


@login_required
def view_task_details(request, task_id):
    """Display the details of a task."""
    user = request.user
    task = get_object_or_404(Task, id=task_id)
    task_checkup = Task_Checkup.objects.filter(task=task).first()
    if request.method == "POST":
        if user.has_perm('tasks.mark_done'):
            task.completed = True
            task.save()
            messages.success(request, "Task marked as done.")
        else:
            messages.error(
                request,
                "You do not have permission to mark this task as done."
                )

    context = {
        "task": task,
        "task_id": task_id,
        "task_checkup": task_checkup,
    }

    return render(request, "tasks/view_task_details.html", context)


@login_required
def add_task(request):
    """Render the add task form."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task added successfully.")
            return redirect("user_task_overview")
    else:
        form = TaskForm()
    context = {
        "form": form,
    }
    return render(request, "tasks/add_task_form.html", context)
