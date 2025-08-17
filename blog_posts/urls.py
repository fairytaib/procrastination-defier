from . import views
from django.urls import path

urlpatterns = [
    path('', views.view_all_posts, name='blog_posts'),
    path('post_details/<int:post_id>/',
         views.view_details,
         name='post_details'),
]
