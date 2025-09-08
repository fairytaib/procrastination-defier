from . import views
from django.urls import path

urlpatterns = [
    path('', views.view_all_posts, name='blog_posts'),
    path('create_post/', views.create_post, name='create_post'),
    path('post_details/<int:post_id>/',
         views.view_details,
         name='post_details'),
    path('delete_post/<int:post_id>/',
         views.delete_post, name='delete_post'),
    path('delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment')
]
