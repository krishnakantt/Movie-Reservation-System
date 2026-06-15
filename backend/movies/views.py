from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Movie, Genre, Showtime, Seat, Screen, Booked
from .serializers import MovieSerializer, GenreSerializer, ShowtimeSerializer, SeatSerializer, ScreenSerializer, BookedSerializer
from accounts.permissions import IsAdmin
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum

# Create your views here.
class GenreListCreateView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
class MovieListCreateView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdmin()]
    
class ShowtimeListCreateView(generics.ListCreateAPIView):
    serializer_class = ShowtimeSerializer
    def get_queryset(self):
        queryset = Showtime.objects.all()
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(show_date=date)
        return queryset
    def validate_showtime(self, data):
        existing = Showtime.objects.filter(
            screen=data['screen'],
            show_date=data['show_date']
        )
        for show in existing:
            if (data['start_time'] < show.end_time and data['end_time'] > show.start_time):
                raise serializers.ValidationError("Showtime overlaps with existing showtime")
        return data
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
class ScreenListCreateView(generics.ListCreateAPIView):
    queryset = Screen.objects.all()
    serializer_class = ScreenSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

class SeatListCreateView(generics.ListCreateAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

class BookedListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        showtime_id = request.data.get('showtime')
        seat_id = request.data.get('seat')
        if Booked.objects.filter(showtime_id=showtime_id, seat_id=seat_id,status='BOOKED').exists():
            return Response({"error": "Seat Already Booked"}, status=400)
        booked = Booked.objects.create(
            user=request.user,
            showtime_id=showtime_id,
            seat_id=seat_id,
        )
        serializer = BookedSerializer(booked)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AvailableSeatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, showtime_id):
        showtime = get_object_or_404(Showtime, id=showtime_id)
        booked_seats = Booked.objects.filter(showtime_id=showtime_id, status='BOOKED').values_list('seat_id', flat=True)
        available_seats = Seat.objects.filter(screen=showtime.screen).exclude(id__in=booked_seats)
        data = []
        for seat in available_seats:
            data.append({
                "id": seat.id,
                "seat_label": f"{seat.row}{seat.number}"
            })
        return Response({"showtime": showtime_id, "available_seats": data})
    
class MyBookingsView(generics.ListAPIView):
    serializer_class = BookedSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Booked.objects.filter(user=self.request.user).order_by('-reserved_at')
    
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, booking_id):
        booking = get_object_or_404(Booked, id=booking_id, user=request.user)
        booking.status = 'CANCELLED'
        booking.save()
        return Response({"message": "Booking Cancelled Successfully"})
    
class AdminReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        if request.user.role != 'Admin':
            return Response({"error": "Unauthorized"}, status=403)
        total_bookings = Booked.objects.count()
        active_bookings = Booked.objects.filter(status='BOOKED').count()
        cancelled_bookings = Booked.objects.filter(status='CANCELLED').count()
        revenue = 0
        booked_tickets = Booked.objects.filter(status='BOOKED')
        for booking in booked_tickets:
            revenue += booking.showtime.ticket_price
        return Response({
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": revenue
        })