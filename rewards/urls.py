from . import views
from django.urls import path

urlpatterns = [
    path('', views.rewards_list, name='rewards_list'),
    path('reward_details/<int:reward_id>/',
         views.view_details,
         name='reward_details'),
    path("rewards/history/", views.order_history, name="rewards_history"),
    path("add_rewards/", views.add_reward, name="add_reward"),
]
