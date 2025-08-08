from . import views
from django.urls import path

urlpatterns = [
    path('', views.view_all_posts, name='view_all_posts'),
    path('post/<int:post_id>/',
         views.view_details,
         name='post_details'),
]
