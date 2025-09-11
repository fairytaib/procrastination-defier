from django import forms
from .models import Comment, Post
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext, ngettext


class CommentForm(forms.ModelForm):
    """Form for adding comments to a blog post."""
    class Meta:
        model = Comment
        fields = ['content']

        widgets = {
            'content': forms.Textarea
            (attrs={'rows': 4, 'placeholder': _('Add a comment...')}),
        }


class PostForm(forms.ModelForm):
    """Form for creating or editing a blog post."""
    class Meta:
        model = Post
        fields = ['title', 'content']

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Post Title')}),
            'content': forms.Textarea(
                attrs={'rows': 12, 'placeholder': _('Post Content')}
                ),
            }
