from . import views
from django.urls import path

urlpatterns = [
    path('', views.subscription_view, name='subscription_view'),
    path('create_subscription/',
         views.create_subscription,
         name='create_subscription'),
    path(
        'your_subscription/',
        views.subscriptions_overview,
        name='subscriptions_overview'
        ),
]
