# Django Imports
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.db import transaction

# App imports
from subscription.utils import can_add_task, refresh_overdue_flags
from subscription.utils import open_tasks_count
from .models import INTERVAL_TO_CHECKUP, Task, Task_Checkup, UserPoints
from .models import FeePaymentBatch
from subscription.models import Subscription
from .forms import TaskForm, CheckTaskForm

# More
from datetime import timedelta
import stripe
from collections import Counter


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def user_task_overview(request):
    """Render a user's task overview page."""
    admin = request.user.has_perm('tasks.mark_done')
    subscription = Subscription.objects.filter(user=request.user).first()
    refresh_overdue_flags(request.user)
    if not admin:
        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
        tasks_undone = Task.objects.filter(
            user=request.user, completed=False,
            fee_to_pay=False, checkup_state=False).order_by('-created_at')
        task_done = Task.objects.filter(
            user=request.user, completed=True).order_by('created_at')
        task_to_check = Task.objects.filter(
            user=request.user, completed=False,
            fee_to_pay=False, checkup_state=True).order_by('-created_at')
        task_with_fee = Task.objects.filter(
            user=request.user,
            completed=False,
            fee_to_pay=True
            ).order_by('-created_at')
        context = {
            'tasks_undone': tasks_undone,
            'tasks_done': task_done[:13],
            'more_tasks_done': task_done[5:],
            'tasks_with_fee': task_with_fee,
            'task_to_check': task_to_check,
            'subscription': subscription,
            'can_add_task': can_add_task(request.user),
            'open_tasks_count': open_tasks_count(request.user),
            'user_points': user_points
        }
    else:
        tasks_undone = Task.objects.filter(completed=False,
                                           fee_to_pay=False,
                                           checkup_state=False).order_by(
            '-user', '-created_at'
            )
        task_to_check = Task.objects.filter(
            completed=False,
            fee_to_pay=False, checkup_state=True).order_by(
                'checkup_date', '-user'
                )
        context = {
            'tasks_undone': tasks_undone,
            'task_to_check': task_to_check,
        }
    return render(request, 'tasks/user_task_overview.html', context)


@login_required
def view_task_details(request, task_id):
    """Display the details of a task."""
    user = request.user
    user_points, _ = UserPoints.objects.get_or_create(
        user=request.user,
        defaults={"points": 0}
    )
    task = get_object_or_404(Task, id=task_id)
    task_checkup = Task_Checkup.objects.filter(
        task=task,
        deleted=False
        ).filter(
        Q(image__isnull=False) |
        Q(video__isnull=False) |
        Q(text_file__isnull=False) |
        Q(audio_file__isnull=False) |
        Q(comments__isnull=False)
    ).order_by('-uploaded_at').first()
    check_form = CheckTaskForm()

    if request.method == "POST":
        if "proof_upload" in request.POST:
            form = CheckTaskForm(request.POST, request.FILES)
            if form.is_valid():
                checkup = form.save(commit=False)
                checkup.task = task
                task.checkup_state = True
                task.save(update_fields=["checkup_state"])
                checkup.save()
                messages.success(
                    request, "Proof uploaded successfully."
                    )
                return redirect("user_task_overview")
            else:
                messages.error(
                    request, "There was an error with your submission."
                    )
        elif "done_checkbox" in request.POST:
            if user.has_perm('tasks.mark_done'):
                task.completed = True
                user_points, _ = UserPoints.objects.get_or_create(
                    user=request.user, defaults={"points": 0}
                )
                user_points.points += task.points or 0
                if task.repetition:
                    task.completed = False
                    task.checkup_date = task.checkup_date + timedelta(
                        days=INTERVAL_TO_CHECKUP[task.interval]
                        )
                task.checkup_state = False
                task.save(update_fields=["checkup_state"])
                task.save(update_fields=["completed"])
                user_points.save(update_fields=["points"])
                messages.success(request, "Task marked as done.")
                return redirect("user_task_overview")
        elif "failed_checkbox" in request.POST:
            if user.has_perm('tasks.mark_done'):
                task.fee_to_pay = True
                if task.repetition:
                    task.completed = False
                    task.checkup_date = task.checkup_date + timedelta(
                        days=INTERVAL_TO_CHECKUP[task.interval]
                        )
                else:
                    task.completed = False
                task.save(update_fields=["fee_to_pay"])
                messages.success(request, "Task marked as failed.")
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
    form = TaskForm(request.POST or None)
    if request.method == "POST":
        if not can_add_task(request.user):
            messages.error(request, "You cannot add more tasks.")
            return redirect("user_task_overview")

        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task added successfully.")
            if 'save_and_add' in request.POST:
                return redirect("add_task")
            else:
                return redirect("user_task_overview")
        else:
            messages.error(
                request,
                "There was an error with your submission. Please try again."
            )
            form = TaskForm()
    context = {
        "form": form,
        'can_add_task': can_add_task(request.user)
    }
    return render(request, "tasks/add_task_form.html", context)


@login_required
def pay_task_fee(request, task_id):
    """Initiate the payment process for a task fee."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if task.completed:
        messages.info(request, "This Task has already been completed.")
        return redirect("user_task_overview")
    if not task.fee_to_pay:
        messages.info(request, "Currently, there is no fee due for this task.")
        return redirect("user_task_overview")

    price_id = settings.STRIPE_FEE_PRICES.get(task.interval)
    if not price_id:
        messages.error(request, "Price ID for this fee is missing.")
        return redirect("user_task_overview")

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=(
            settings.DOMAIN
            + reverse('pay_task_fee_success', args=[task.id])
            + '?session_id={CHECKOUT_SESSION_ID}'
        ),
        cancel_url=settings.DOMAIN + reverse('user_task_overview'),
        customer_email=(request.user.email or None),
        payment_intent_data={
            'metadata': {'task_id': task.id, 'user_id': request.user.id}
        },
        metadata={'task_id': task.id, 'user_id': request.user.id},
    )

    task.fee_payment_session_id = session.id
    task.save(update_fields=['fee_payment_session_id'])
    return redirect(session.url, code=303)


@login_required
def pay_task_fee_success(request, task_id):
    """Handle successful payment for a task fee."""
    session_id = request.GET.get('session_id')
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if not session_id or session_id != task.fee_payment_session_id:
        messages.error(request, "Session could not be verified.")
        return redirect('user_task_overview')

    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != 'paid':
        messages.warning(request, "Payment not yet confirmed.")
        return redirect('user_task_overview')

    # Remove lock flag and close task (no points awarded!)
    if task.repetition:
        # Release slot again, but leave task active and reschedule
        task.fee_to_pay = False
        task.completed = False
        task.penalty_paid_at = timezone.now()
        # Set next checkup:
        task.checkup_date = timezone.now().date() + timedelta(
            days=INTERVAL_TO_CHECKUP[task.interval])
        task.save(update_fields=[
            'fee_to_pay', 'completed', 'penalty_paid_at', 'checkup_date'])
    else:
        task.fee_to_pay = False
        task.completed = True
        task.penalty_paid_at = timezone.now()
        task.save(update_fields=['fee_to_pay', 'completed', 'penalty_paid_at'])

    messages.success(request, "Fee paid. Task closed.")
    return redirect('user_task_overview')


@login_required
def pay_all_fees(request):
    """Initiate the payment process for all task fees."""
    qs = Task.objects.filter(
        user=request.user, completed=False, fee_to_pay=True).order_by("id")
    if not qs.exists():
        messages.info(request, "No fees open.")
        return redirect("user_task_overview")

    counts = Counter(qs.values_list("interval", flat=True))
    line_items = []
    for interval, qty in counts.items():
        price_id = settings.STRIPE_FEE_PRICES.get(interval)
        if not price_id:
            messages.error(
                request, f"Price for interval '{interval}' is not configured.")
            return redirect("user_task_overview")
        line_items.append({"price": price_id, "quantity": qty})

    batch = FeePaymentBatch.objects.create(user=request.user, status="created")

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=(
            settings.DOMAIN
            + reverse("pay_all_fees_success")
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=settings.DOMAIN + reverse("user_task_overview"),
        customer_email=(request.user.email or None),
        metadata={"batch_id": str(batch.id), "user_id": request.user.id},
    )

    batch.session_id = session.id
    batch.tasks.set(qs)
    batch.save(update_fields=["session_id"])

    return redirect(session.url, code=303)


@login_required
def pay_all_fees_success(request):
    """Handle successful payment for all task fees."""
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Session is missing.")
        return redirect("user_task_overview")

    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        messages.warning(request, "Payment not yet confirmed.")
        return redirect("user_task_overview")

    # find Batch
    batch = get_object_or_404(
        FeePaymentBatch, user=request.user, session_id=session_id
    )
    if batch.status == "paid":
        messages.info(request, "The batch has already been processed.")
        return redirect("user_task_overview")

    # Unlock/complete all tasks in the batch
    now = timezone.now()
    with transaction.atomic():
        batch = (FeePaymentBatch.objects
                 .select_for_update()
                 .get(user=request.user, session_id=session_id))

        if batch.status == "paid":
            messages.info(request, "The batch has already been processed.")
            return redirect("user_task_overview")

        for task in batch.tasks.select_for_update():
            task.fee_to_pay = False
            task.penalty_paid_at = now
            if task.repetition:
                from datetime import timedelta
                task.completed = False
                task.checkup_date = timezone.now().date() + timedelta(
                    days=INTERVAL_TO_CHECKUP[task.interval]
                    )
                task.save(
                    update_fields=[
                        "fee_to_pay",
                        "penalty_paid_at",
                        "completed",
                        "checkup_date"
                        ]
                    )
            else:
                task.completed = True
                task.save(
                    update_fields=[
                        "fee_to_pay", "penalty_paid_at", "completed"
                        ]
                    )

    batch.status = "paid"
    batch.paid_at = now
    batch.save(update_fields=["status", "paid_at"])

    messages.success(request, "All open fees have been paid.")
    return redirect("user_task_overview")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("user_task_overview")
    # We won't render a separate page; POST only from the inline modal.
    return redirect("view_task_details", task_id=task_id)
