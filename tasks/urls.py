from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.user_task_overview, name='user_task_overview'),
]
