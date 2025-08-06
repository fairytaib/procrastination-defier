from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', views.rewards_list, name='rewards_list'),
]
