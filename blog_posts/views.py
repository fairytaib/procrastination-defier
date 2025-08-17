from django.shortcuts import render, get_object_or_404
from .models import Post, Comment


def view_all_posts(request):
    posts = Post.objects.all()
    return render(request, "blog_posts/all_posts.html", {"posts": posts})


def view_details(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    return render(
        request, "blog_posts/post_details.html",
        {"post": post, "comments": comments}
    )
