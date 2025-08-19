from django import forms
from .models import Task, Task_Checkup
from datetime import date
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
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
        fields = ['comments',
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
        f = self.cleaned_data.get('image')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        try:
            # 1. Format auslesen
            with Image.open(f) as im:
                fmt = (im.format or '').lower()
            # 2. Integrität prüfen (separat, da verify() das File schließt)
            with Image.open(f) as im:
                im.verify()
        except (UnidentifiedImageError, Exception):
            raise ValidationError("Uploaded file is not a valid image.")

        if fmt not in {'jpeg', 'jpg', 'png', 'webp'}:
            raise ValidationError("Only JPEG, JPG, PNG or WEBP images are allowed.")
        return f

    def clean_text_file(self):
        f = self.cleaned_data.get('text_file')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        ct  = getattr(f, 'content_type', '')
        allowed_ext = {'pdf','txt','docx'}
        allowed_ct  = {
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        if ext not in allowed_ext and ct not in allowed_ct:
            raise ValidationError("Only PDF, TXT or DOCX files are allowed.")
        return f

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if not audio_file:
            return None

        allowed_ct = {'audio/mpeg', 'audio/wav'}
        if getattr(audio_file, 'content_type', None) not in allowed_ct:
            raise ValidationError("Only MP3 or WAV files are allowed.")
        return audio_file
