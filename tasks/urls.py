from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.user_task_overview, name='user_task_overview'),
    path('task_details/<int:task_id>/',
         views.view_task_details,
         name='view_task_details'),
]
