from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket
from .serializers import (
    CreateTicketSerializer,
    TicketAnswerSerializer,
    TicketSerializer,
    TicketCompletedSerializer,
)
from rest_framework.permissions import IsAuthenticated
from user.models import User
from user.permissions import IsTypeOneUser
from django.utils import timezone


class TicketCreate(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CreateTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, ticket_status="Pending")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketClient(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        user = User.objects.get(email=request.user)
        tickets = Ticket.objects.filter(created_by=user)
        serializer = TicketSerializer(tickets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminTicket(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request, format=None):

        if request.data["type"] == "All":

            tickets = Ticket.objects.all()
            serializer = TicketSerializer(tickets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:

            tickets = Ticket.objects.filter(ticket_status=request.data["type"])
            serializer = TicketSerializer(tickets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminTicketAnswerCreate(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        serializer = TicketAnswerSerializer(data=request.data)

        if serializer.is_valid():

            ticket_id = serializer.validated_data["ticket"].id
            ticket = Ticket.objects.get(id=ticket_id)

            if ticket.ticket_status != "Completed":

                if ticket.ticket_status == "Pending":
                    ticket.ticket_status = "Active"
                    ticket.assigned_to = request.user
                    ticket.accepted_date = timezone.now()
                    ticket.save()
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientTicketAnswerCreate(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = TicketAnswerSerializer(data=request.data)

        if serializer.is_valid():

            ticket_id = serializer.validated_data["ticket"].id

            ticket = Ticket.objects.get(id=ticket_id)

            if ticket.ticket_status != "Completed":

                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteTicket(APIView):

    permission_classes = [IsAuthenticated, IsTypeOneUser]

    def post(self, request):

        serializer = TicketCompletedSerializer(data=request.data)

        if serializer.is_valid():

            ticket = Ticket.objects.get(id=request.data["id"])

            if ticket.ticket_status != "Completed":

                ticket.ticket_status = "Completed"
                ticket.closed_date = timezone.now()
                ticket.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
