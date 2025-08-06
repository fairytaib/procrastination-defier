from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.rewards_list, name='rewards_list'),
    path('reward_details/<int:reward_id>/',
         views.view_details,
         name='reward_details'),
]
