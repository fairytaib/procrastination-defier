from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Reward, RewardHistory
from tasks.models import UserPoints
from django.contrib.auth.models import User
from .forms import RewardForm
from django.contrib import messages
from django.utils.translation import gettext as _


# Fallback-Mapping for Old stocks (ISO2 -> Name) + Special values
COUNTRY_CODE_TO_NAME = {
    'DE': _('Germany'),
    'FR': _('France'),
    'BE': _('Belgium'),
    'CH': _('Switzerland'),
    'DK': _('Denmark'),
    'FI': _('Finland'),
    'SE': _('Sweden'),
    'NO': _('Norway'),
    'NL': _('Netherlands'),
    'IT': _('Italy'),
    'ES': _('Spain'),
    'NOLIMIT': _('Everywhere'),
}
NAME_TO_CODE = {v: k for k, v in COUNTRY_CODE_TO_NAME.items()}


def rewards_list(request):
    """View to display a list of rewards."""
    rewards = Reward.objects.all()

    selected_type = (
        request.GET.get(
            'type'
            ) or request.GET.get('reward_type') or '').strip()
    selected_country = (
        request.GET.get('country'
                        ) or request.GET.get(
                            'available_countries'
                            ) or '').strip()
    selected_sort = (request.GET.get('sort') or '').strip()
    type_field = 'reward_type'
    countries_field = 'available_countries'

    type_choices = list(Reward._meta.get_field(type_field).choices or [])
    reward_type_options = [{'value': v, 'label': l} for (v, l) in type_choices]

    country_choices = list(
        Reward._meta.get_field(countries_field).choices or []
        )
    if not country_choices:
        country_choices = [(code, COUNTRY_CODE_TO_NAME.get(code, code))
                           for code in sorted(COUNTRY_CODE_TO_NAME.keys())]
    country_options = [{'value': v, 'label': l} for (v, l) in country_choices]

    if selected_type:
        rewards = rewards.filter(**{type_field: selected_type})

    if selected_country:
        values_to_match = {selected_country}
        if selected_country in NAME_TO_CODE:          # Name -> Code
            values_to_match.add(NAME_TO_CODE[selected_country])
        if selected_country in COUNTRY_CODE_TO_NAME:  # Code -> Name
            values_to_match.add(COUNTRY_CODE_TO_NAME[selected_country])

        q = Q()
        for val in values_to_match:
            q |= Q(**{f"{countries_field}__contains": val})
        rewards = rewards.filter(q)

    price_field = 'cost'
    if selected_sort == 'price_asc':
        rewards = rewards.order_by(price_field)
    elif selected_sort == 'price_desc':
        rewards = rewards.order_by(f"-{price_field}")
    is_filtered = bool(selected_type or selected_country)

    context = {
        'rewards': rewards,
        'reward_types': reward_type_options,
        'countries': country_options,
        'selected_type': selected_type,
        'selected_country': selected_country,
        'selected_sort': selected_sort,
        'is_filtered': is_filtered,
    }

    return render(request, 'rewards/rewards_list.html', context)


def view_details(request, reward_id):
    """Display the details of a reward."""
    reward = get_object_or_404(Reward, id=reward_id)
    user = request.user
    if request.user.is_authenticated:
        user_points = UserPoints.objects.filter(user=user).first()
        context = {
            "reward": reward,
            "reward_id": reward_id,
            "user_points": user_points if user_points else 0}
    else:
        context = {
            "reward": reward,
            "reward_id": reward_id,
        }

    return render(request, "rewards/view_reward_details.html", context)


@login_required
def add_reward(request):
    """Render the add reward form."""
    form = RewardForm(request.POST or None)
    user = request.user
    if request.method == "POST":
        if user.has_perm('tasks.mark_done'):
            if form.is_valid():
                reward = form.save(commit=False)
                reward.save()
                messages.success(request, _("Reward added successfully."))
                if 'save_and_add' in request.POST:
                    return redirect("add_reward")
                else:
                    return redirect("rewards_list")
            else:
                form = RewardForm()
                messages.warning(
                    request,
                    _("Failed to add reward. Please correct the errors below.")
                )
        else:
            messages.warning(
                request, _("You do not have permission to add rewards.")
            )
            return redirect("rewards_list")
    context = {
        "form": form,
    }
    return render(request, "rewards/add_reward_form.html", context)


@login_required
def delete_reward(request, reward_id):
    """Delete a reward."""
    reward = get_object_or_404(Reward, id=reward_id)
    if request.method == "POST":
        if not request.user.has_perm('tasks.mark_done'):
            messages.warning(
                request, _("You do not have permission to delete rewards.")
            )
            return redirect("rewards_list")
        reward.delete()
        messages.success(request, _("Reward deleted successfully."))
        return redirect("rewards_list")
    # We won't render a separate page; POST only from the inline modal.
    return redirect("view_reward_details", reward_id=reward_id)


@login_required
def edit_reward(request, reward_id):
    """Edit a reward."""
    reward = get_object_or_404(Reward, id=reward_id)
    form = RewardForm(instance=reward)

    if request.method == "POST":
        form = RewardForm(request.POST, request.FILES, instance=reward)
        if not request.user.has_perm('tasks.mark_done'):
            messages.warning(
                request, _("You do not have permission to edit rewards.")
            )
            return redirect("rewards_list")
        if form.is_valid():
            form.save()
            messages.success(request, _("Reward updated successfully."))
            return redirect("view_reward_details", reward_id=reward.id)
    return render(request, "rewards/edit_reward_form.html", {
        "form": form, "reward": reward
        })


@login_required
def order_history(request):
    """View to display the order history of rewards."""
    rewards = (RewardHistory.objects.filter(
            reward_sent=False).order_by('-bought_at'))

    paginator = Paginator(rewards, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "rewards": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "rewards/reward_history.html", context)
