from django.shortcuts import render
from .models import Post, Comment


def view_all_posts(request):
    posts = Post.objects.all()
    return render(request, "blog_posts/all_posts.html", {"posts": posts})


def view_details(request, post_id):
    post = Post.objects.get(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    return render(
        request, "blog_posts/post_details.html",
        {"post": post, "comments": comments}
    )
