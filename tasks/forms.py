from email.mime import image
from django import forms
from .models import Task, Task_Checkup
from datetime import date
from django.core.exceptions import ValidationError
import re


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title',
                  'description',
                  'goal_description',
                  'repetition',
                  'interval']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not re.match(r'^[A-Za-z0-9\s]+$', title):
            raise ValidationError(
                "Title can only contain letters, numbers, and spaces.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise ValidationError(
                "Description must be at least 10 characters long.")
        return description

    def clean_goal_description(self):
        goal_description = self.cleaned_data.get('goal_description')
        if len(goal_description) < 10:
            raise ValidationError(
                "Goal description must be at least 10 characters long.")
        return goal_description


class CheckTaskForm(forms.ModelForm):
    class Meta:
        model = Task_Checkup
        fields = ['task',
                  'comments',
                  'image',
                  'text_file',
                  'audio_file']

        labels = {
                'image': 'Image Proof (JPEG, PNG, JPG or WEBP)',
                'text_file': 'Text File Proof (TXT, DOCX, PDF)',
                'audio_file': 'Audio File Proof (MP3, WAV)',
            }

        widgets = {
            'image': forms.FileInput(
                attrs={'class': 'form-control-file'}),
            'text_file': forms.FileInput(
                attrs={'class': 'form-control-file'}),
            'audio_file': forms.FileInput(
                attrs={'class': 'form-control-file'}),
        }

        def __init__(self, *args, **kwargs):
            """Initialize the form and set CSS classes for fields."""
            super().__init__(*args, **kwargs)
            self.fields[
                'image',
                'text_file',
                'audio_file'
            ].widget.attrs['class'] = 'form-control-file'

        def clean_image(self):
            """Validate the uploaded image file."""
            image = self.cleaned_data.get('image')

            if not image or not hasattr(image, 'file') or image.size == 0:
                return None

            try:
                img = image.open(image)
                img.verify()
            except Exception:
                raise ValidationError("Uploaded file is not a valid image.")

            allowed_types = ['jpeg', 'png', 'jpg', 'webp']
            if img.format.lower() not in allowed_types:
                raise ValidationError(
                    f"Only {', '.join(allowed_types)} images are allowed.")

            return image

        def clean_text_file(self):
            """Validate the uploaded text file."""
            text_file = self.cleaned_data.get('text_file')

            if not text_file or not hasattr(
                    text_file, 'file') or text_file.size == 0:
                return None

            try:
                img = text_file.open(text_file)
                img.verify()
            except Exception:
                raise ValidationError("Uploaded file is not a valid image.")

            allowed_types = ['jpeg', 'png', 'jpg', 'webp']
            if img.format.lower() not in allowed_types:
                raise ValidationError(
                    f"Only {', '.join(allowed_types)} images are allowed.")

            return text_file
