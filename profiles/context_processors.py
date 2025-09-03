from .models import UserProfile


def user_profile_context(request):
    """Add user profile information to the context."""
    if not request.user.is_authenticated:
        return {"user_profile": None}

    user_profile = (
        UserProfile.objects
        .filter(user=request.user)
        .first()
    )
    return {"user_profile": user_profile}
