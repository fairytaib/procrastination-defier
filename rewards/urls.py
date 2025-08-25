from . import views
from django.urls import path

urlpatterns = [
    path('', views.rewards_list, name='rewards_list'),
    path('reward_details/<int:reward_id>/',
         views.view_details,
         name='reward_details'),
    path('reward_checkout/<int:reward_id>/',
         views.redeem_checkout, name='redeem_checkout'),
]
