from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_user_profile, name='view_user_profile'),
    path('account/update/', views.account_update, name='account_update'),
]
