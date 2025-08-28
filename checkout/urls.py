from django.urls import path
from . import views


urlpatterns = [
    path('<int:reward_id>/', views.place_order, name='place_order'),
    path('all/', views.user_order_overview, name='user_order_overview')
]
