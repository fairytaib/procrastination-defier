from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from subscription.utils import can_add_task
from .models import INTERVAL_TO_CHECKUP, Task, Task_Checkup, UserPoints
from subscription.models import Subscription
from .forms import TaskForm, CheckTaskForm


@login_required
def user_task_overview(request):
    """Render a user's task overview page."""
    admin = request.user.has_perm('tasks.mark_done')
    subscription = Subscription.objects.filter(user=request.user).first()
    if not admin:
        tasks_undone = Task.objects.filter(
            user=request.user, completed=False).order_by('-created_at')
        task_done = Task.objects.filter(
            user=request.user, completed=True).order_by('created_at')
        context = {
            'tasks_undone': tasks_undone,
            'tasks_done': task_done,
            'subscription': subscription,
            'can_add_task': can_add_task(request.user)
        }
    else:
        tasks_undone = Task.objects.filter(completed=False).order_by(
            '-user', '-created_at'
            )
        context = {
            'tasks_undone': tasks_undone,
        }
    return render(request, 'tasks/user_task_overview.html', context)


@login_required
def view_task_details(request, task_id):
    """Display the details of a task."""
    user = request.user
    user_points = UserPoints.objects.filter(user=user).first()
    task = get_object_or_404(Task, id=task_id)
    task_checkup = Task_Checkup.objects.filter(
        task=task
        ).order_by('-uploaded_at').first()
    check_form = CheckTaskForm()

    if request.method == "POST":
        if "proof_upload" in request.POST:
            form = CheckTaskForm(request.POST, request.FILES)
            if form.is_valid():
                checkup = form.save(commit=False)
                checkup.task = task
                checkup.save()
                messages.success(
                    request, "Proof uploaded successfully."
                    )
                return redirect("user_task_overview")
        elif "done_checkbox" in request.POST:
            if user.has_perm('tasks.mark_done'):
                task.completed = True
                user_points.points += task.points or 0
                if task.repetition:
                    task.completed = False
                    task.checkup_date = task.checkup_date + timedelta(
                        days=INTERVAL_TO_CHECKUP[task.interval]
                        )
                else:
                    task.completed = False
                task.save(update_fields=["completed"])
                user_points.save(update_fields=["points"])
                messages.success(request, "Task marked as done.")
                return redirect("user_task_overview")
            else:
                messages.error(
                    request,
                    "You do not have permission to mark this task as done."
                    )

    context = {
        "task": task,
        "task_id": task_id,
        "task_checkup": task_checkup,
        "check_form": check_form,
    }

    return render(request, "tasks/view_task_details.html", context)


@login_required
def add_task(request):
    """Render the add task form."""
    if request.method == "POST":
        if not can_add_task(request.user):
            messages.error(request, "You cannot add more tasks.")
            return redirect("user_task_overview")
        else:
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
