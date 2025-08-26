from . import views
from django.urls import path

urlpatterns = [
    path('', views.view_all_posts, name='blog_posts'),
    path('create_post/', views.create_post, name='create_post'),
    path('post_details/<int:post_id>/',
         views.view_details,
         name='post_details'),
]
