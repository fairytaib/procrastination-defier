from . import views
from django.urls import path

urlpatterns = [
    path('', views.subscription_view, name='subscription_view'),
]
