from django.shortcuts import render


def subscriprion_view(request):
    """ A view to return the subscription page """
    return render(request, 'subscription/subscription.html')