from django.urls import path
from . import views


urlpatterns = [
    path('<int:reward_id>/', views.place_order, name='place_order'),
    path('all/', views.user_order_overview, name='user_order_overview'),
    path('order/<int:order_id>/',
         views.view_order_details, name='view_order_details'),
    path('order_history/', views.order_history, name='order_history'),
]
