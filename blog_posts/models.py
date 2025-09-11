from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """Model representing a blog post."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False, blank=False)
    content = models.TextField(max_length=2000, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Model representing a comment on a blog post."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
        )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
