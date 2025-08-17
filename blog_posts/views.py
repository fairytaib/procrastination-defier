from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from .forms import CommentForm
from django.shortcuts import redirect
from django.contrib import messages


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
