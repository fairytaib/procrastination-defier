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
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(max_length=500, blank=False, null=False)
    goal_description = models.TextField(
        max_length=500,
        help_text="Describe the goal of this task.",
        blank=False, null=False
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    repetition = models.BooleanField(default=False)
    interval = models.CharField(max_length=10,
                                choices=INTERVAL,
                                default='weekly')
    fee = models.DecimalField(max_digits=10, decimal_places=2, blank=False,
                              null=False,
                              help_text="Fee for failing this task.")
    fee_to_pay = models.BooleanField(default=False)
    fee_payment_session_id = models.CharField(
        max_length=255, blank=True, null=True
    )
    penalty_paid_at = models.DateTimeField(blank=True, null=True)
    points = models.PositiveIntegerField(
        blank=False,
        null=False,
        help_text="Points awarded for completing this task."
    )
    checkup_state = models.BooleanField(default=False)
    checkup_date = models.DateField(
        help_text="Next checkup date for this task.",
        null=True, blank=True
    )

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
        return f"{self.title} (User: {self.user.username}),{self.checkup_date}"

    @property
    def due_in_days(self):
        if self.checkup_date:
            return (self.checkup_date - date.today()).days
        return None

    @property
    def is_due_soon(self):
        d = self.due_in_days
        return d is not None and d <= 2

        def __str__(self):
            return self.title


class Task_Checkup(models.Model):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='checkups')
    image = CloudinaryField(
        resource_type='image', blank=True, null=True,
        help_text="Upload an image for this checkup."
    )
    text_file = CloudinaryField(
        resource_type='raw', blank=True, null=True,
        help_text="Upload a text file for this checkup."
    )
    audio_file = CloudinaryField(
        resource_type='video', blank=True, null=True,
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
        mapping = {
            'image': 'image',
            'text_file': 'raw',
            'audio_file': 'video',
        }
        for field, rtype in mapping.items():
            f = getattr(self, field)
            if f and getattr(f, 'public_id', None):
                destroy(f.public_id, resource_type=rtype)
                setattr(self, field, None)
        self.deleted = True
        self.save()


class FeePaymentBatch(models.Model):
    """Model representing a batch of fee payments for tasks."""
    STATUS_CHOICES = [
        ("created", "created"), ("paid", "paid"), ("canceled", "canceled")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tasks = models.ManyToManyField("Task", related_name="fee_batches")
    session_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created"
        )
    amount_cents = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Batch #{self.id} for {self.user} ({self.status})"
