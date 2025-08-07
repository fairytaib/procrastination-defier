from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from cloudinary.models import CloudinaryField

INTERVAL = (
    ('weekly', 'Weekly'),
    ('biweekly', 'Biweekly'),
    ('monthly', 'Monthly'),
)

INTERVAL_TO_CHECKUP = {
    'weekly': 7,
    'biweekly': 14,
    'monthly': 30,
}

INTERVAL_TO_FEE = {
    'weekly': 0.70,
    'biweekly': 1.40,
    'monthly': 2.10,
}

INTERVAL_TO_POINTS = {
    'weekly': 10,
    'biweekly': 20,
    'monthly': 40,
}


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='points')
    points = models.PositiveIntegerField(
        help_text="Total points earned by the user."
        )

    def __str__(self):
        return f"{self.user.username} - {self.points} points"


class Task(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    goal_description = models.TextField(
        max_length=500,
        help_text="Describe the goal of this task."
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    repetition = models.BooleanField(default=False)
    interval = models.CharField(max_length=10,
                                choices=INTERVAL,
                                default='weekly')
    fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True,
                              null=True,
                              help_text="Fee for failing this task.")
    points = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Points awarded for completing this task."
    )
    checkup_date = models.DateField(
        help_text="Next checkup date for this task.",
        null=True, blank=True
    )
    # user_comments = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        '''Override save method to set fee,
        points and checkup_date based on interval'''
        if self.interval in dict(INTERVAL):
            self.fee = INTERVAL_TO_FEE[self.interval]
            self.points = INTERVAL_TO_POINTS[self.interval]
            self.checkup_date = date.today() + timedelta(
                days=INTERVAL_TO_CHECKUP[self.interval]
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Task_Checkup(models.Model):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='checkups')
    image = CloudinaryField(
        'image', blank=True, null=True,
        help_text="Upload an image for this checkup."
    )
    text_file = CloudinaryField(
        'text_file', blank=True, null=True,
        help_text="Upload a text file for this checkup."
    )
    audio_file = CloudinaryField(
        'audio_file', blank=True, null=True,
        help_text="Upload an audio file for this checkup."
    )
    comments = models.TextField(
        blank=True, null=True,
        help_text="Add any comments for this checkup."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    delete_after_days = models.PositiveIntegerField(default=30)
    deleted = models.BooleanField(default=False)

    def should_be_deleted(self):
        return (date.today() - self.uploaded_at).days >= self.delete_after_days

    def delete_files(self):
        from cloudinary.uploader import destroy
        for field in ['image', 'text_file', 'audio_file']:
            file = getattr(self, field)
            if file:
                destroy(file.public_id, resource_type=file.resource_type)
                setattr(self, field, None)
        self.deleted = True
        self.save()
