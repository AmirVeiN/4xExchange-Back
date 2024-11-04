from rest_framework import serializers
from .models import Ticket, TicketAnswer

class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("title", "description")


class TicketAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAnswer
        fields = ["ticket", "userType", "message", "time"]


class TicketSerializer(serializers.ModelSerializer):
    ticket = TicketAnswerSerializer(many=True, read_only=True)
    email = serializers.EmailField(source="created_by.email")

    class Meta:
        model = Ticket
        fields = [
            "id",
            "email",
            "title",
            "description",
            "created_by",
            "date_created",
            "assigned_to",
            "accepted_date",
            "closed_date",
            "ticket_status",
            "ticket",
        ]

class TicketCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id"]
