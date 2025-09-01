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
    path('change_plan/', views.change_plan, name='subscription_change'),
    path('cancel_plan/', views.cancel_plan, name='subscription_cancel'),
    path('resume_plan/', views.resume_plan, name='subscription_resume'),
]
