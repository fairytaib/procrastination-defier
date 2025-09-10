from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def view_all_posts(request):
    posts = Post.objects.all()
    return render(request, "blog_posts/all_posts.html", {"posts": posts})


def view_details(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    comment_form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(
                    request, "Comment posted successfully."
                    )
            return redirect("post_details", post_id=post.id)
        else:
            messages.error(
                    request, "Failed to post comment."
                    )
            return redirect("post_details", post_id=post.id)

    context = {
        "post": post,
        "comments": comments,
        "form": comment_form

    }

    return render(
        request, "blog_posts/post_details.html",
        context
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("post_details", post_id=post.id)
        else:
            messages.error(request, "Failed to create post.")
    else:
        form = PostForm()

    context = {
        "form": form
    }

    return render(request, "blog_posts/create_post.html", context)


@login_required
def delete_post(request, post_id):
    """ Delete a post if the logged-in user is the author.
    """
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("blog_posts")
    # We won't render a separate page; POST only from the inline modal.
    return redirect("blog_posts")


@login_required
def delete_comment(request, comment_id):
    """ Delete a comment if the logged-in user is the author."""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect("post_details", post_id=comment.post.id)
    # We won't render a separate page; POST only from the inline modal.
    return redirect("blog_posts")
