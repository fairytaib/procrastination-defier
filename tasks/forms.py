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
