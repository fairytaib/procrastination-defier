from django import forms
from .models import Task, Task_Checkup
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
import re
from django.utils.translation import gettext_lazy as _


TASKS_MAX_UPLOAD_SIZES = {
    'image': 5 * 1024 * 1024,        # 5 MB
    'text_file': 10 * 1024 * 1024,   # 10 MB
    'audio_file': 20 * 1024 * 1024,  # 20 MB
    'video': 100 * 1024 * 1024,  # 100 MB
}


def _mb(bytes_):
    return int(bytes_ / (1024*1024))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title',
                  'description',
                  'goal_description',
                  'repetition',
                  'interval']

        labels = {
            'title': _('Task Title'),
            'description': _('Task Description'),
            'goal_description': _('Goal Description'),
            'repetition': _('Is this a repeating task?'),
            'interval': _('When do you want this task checked?'),
        }

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('Task Title')}
                ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder':
                    _('Describe the task as detailed as possible'),
                    'rows': 3}
                ),
            'goal_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder':
                    _('Describe what you want to achieve so we can check if you made it'),
                    'rows': 3}
                ),
            'repetition': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
                ),
            'interval': forms.Select(
                attrs={'class': 'form-select'}
                ),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not re.match(r'^[A-Za-z0-9\s]+$', title):
            raise ValidationError(
                _("Title can only contain letters, numbers, and spaces.")
            )
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise ValidationError(
                _("Description must be at least 10 characters long.")
            )
        return description

    def clean_goal_description(self):
        goal_description = self.cleaned_data.get('goal_description')
        if len(goal_description) < 10:
            raise ValidationError(
                _("Goal description must be at least 10 characters long.")
            )
        return goal_description


class CheckTaskForm(forms.ModelForm):
    class Meta:
        model = Task_Checkup
        fields = ['comments',
                  'image',
                  'video',
                  'text_file',
                  'audio_file']

        labels = {
                'image': _('Image Proof (JPEG, PNG, JPG or WEBP)'),
                'video': _('Video Proof (MP4, WEBM, MOV, AVI, MKV or MPEG)'),
                'text_file': _('Text File Proof (TXT, DOCX, PDF)'),
                'audio_file': _('Audio File Proof (MP3, WAV)'),
            }

        widgets = {
            'comments': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(
                attrs={'class': 'form-control'}),
            'video': forms.FileInput(
                attrs={'class': 'form-control'}),
            'text_file': forms.FileInput(
                attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(
                attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = (
            f"Upload an image for this checkup – max {
                _mb(TASKS_MAX_UPLOAD_SIZES['image'])} MB"
        )
        self.fields['video'].help_text = (
            f"Upload a video for this checkup – max {
                _mb(TASKS_MAX_UPLOAD_SIZES['video'])} MB"
        )
        self.fields['text_file'].help_text = (
            f"Upload a text file for this checkup – max {
                _mb(TASKS_MAX_UPLOAD_SIZES['text_file'])} MB"
        )
        self.fields['audio_file'].help_text = (
            f"Upload an audio file for this checkup – max {
                _mb(TASKS_MAX_UPLOAD_SIZES['audio_file'])} MB"
        )

    def _validate_size(self, f, kind: str):
        """Validate the size of an uploaded file."""
        if not f:
            return
        max_bytes = TASKS_MAX_UPLOAD_SIZES.get(kind)
        if max_bytes and getattr(f, 'size', 0) > max_bytes:
            mb = int(max_bytes / (1024 * 1024))
            raise ValidationError(_(
                f"File too large. Max allowed for {kind} is {mb} MB."
            ))

    def clean_image(self):
        """Validate uploaded image file type."""
        f = self.cleaned_data.get('image')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        try:
            with Image.open(f) as im:
                fmt = (im.format or '').lower()
            with Image.open(f) as im:
                im.verify()
        except (UnidentifiedImageError, Exception):
            raise ValidationError(_("Uploaded file is not a valid image."))

        if fmt not in {'jpeg', 'jpg', 'png', 'webp'}:
            raise ValidationError(
                _("Only JPEG, JPG, PNG or WEBP images are allowed.")
            )
        self._validate_size(f, 'image')
        return f

    def clean_video(self):
        """Validate uploaded video file type."""
        f = self.cleaned_data.get('video')
        if not f:
            return None

        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        ct = getattr(f, 'content_type', '')

        allowed_ext = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'mpeg', 'mpg'}
        allowed_ct = {
            'video/mp4', 'video/webm', 'video/quicktime',  # mov
            'video/x-msvideo',                             # avi
            'video/x-matroska', 'video/mpeg'
        }

        if ext not in allowed_ext and ct not in allowed_ct:
            raise ValidationError(
                _("Only MP4, WEBM, MOV, AVI, MKV or MPEG are allowed.")
            )

        self._validate_size(f, 'video')
        return f

    def clean_text_file(self):
        """Validate uploaded text file type."""
        f = self.cleaned_data.get('text_file')
        if not f or getattr(f, 'size', 0) == 0:
            return None
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        ct = getattr(f, 'content_type', '')
        allowed_ext = {'pdf', 'txt', 'docx'}
        allowed_ct = {
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        if ext not in allowed_ext and ct not in allowed_ct:
            raise ValidationError(
                _("Only PDF, TXT or DOCX files are allowed.")
            )
        self._validate_size(f, 'text_file')
        return f

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if not audio_file:
            return None

        allowed_ct = {'audio/mpeg', 'audio/wav'}
        if getattr(audio_file, 'content_type', None) not in allowed_ct:
            raise ValidationError(_("Only MP3 or WAV files are allowed."))
        self._validate_size(audio_file, 'audio_file')
        return audio_file
