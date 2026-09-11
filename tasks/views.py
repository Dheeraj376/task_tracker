from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class task_tracker_dashboard(models.Model):

    # Priority options
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    # Status options
    class Status(models.TextChoices):
        TO_DO = "TO_DO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    task_name = models.CharField(
        max_length=100,
        blank=False
    )

    task_description = models.CharField(
        max_length=500,
        blank=True
    )

    task_assignee = models.CharField(
        max_length=50,
        blank=False
    )

    task_priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        blank=False
    )

    task_status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TO_DO
    )

    task_due_date = models.DateField()

    task_created_at = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):
        if self.task_due_date < timezone.localdate():
            raise ValidationError({
                "task_due_date": "Due date must be today or a future date."
            })

    def __str__(self):
        return self.task_name


   