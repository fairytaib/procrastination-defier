from django import forms
from .models import Task, Task_Checkup
from datetime import date
from django.core.exceptions import ValidationError
from PIL import Image
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
            'image'
        ].widget.attrs['class'] = 'form-control-file'
        self.fields[
            'text_file'
        ].widget.attrs['class'] = 'form-control-file'
        self.fields[
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
            text_file = text_file.open(text_file)
            text_file.verify()
        except Exception:
            raise ValidationError("Uploaded file is not a valid text file.")

        allowed_types = {'pdf'}
        allowed_cts = {'application/pdf'}
        ct = getattr(text_file, 'content_type', None)
        ext = text_file.name.rsplit(
            '.', 1
            )[-1].lower() if '.' in text_file.name else ''

        if (ct not in allowed_cts) and (ext not in allowed_types):
            raise ValidationError("Only PDF files are allowed.")

        return text_file

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if not audio_file:
            return None

        allowed_ct = {'audio/mpeg', 'audio/wav'}
        if getattr(audio_file, 'content_type', None) not in allowed_ct:
            raise ValidationError("Only MP3 or WAV files are allowed.")
        return audio_file