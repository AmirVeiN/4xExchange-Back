import uuid
from django.db import models
from user.models import User


class Ticket(models.Model):

    status_choices = (
        ("Active", "Active"),
        ("Completed", "Completed"),
        ("Pending", "Pending"),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_by"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    accepted_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    ticket_status = models.CharField(max_length=15, choices=status_choices)

    def __str__(self):
        return self.title


class TicketAnswer(models.Model):

    status_choices = (
        ("Admin", "Admin"),
        ("Client", "Client"),
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="ticket")
    userType = models.CharField(max_length=15, choices=status_choices)
    message = models.TextField(max_length=400)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
