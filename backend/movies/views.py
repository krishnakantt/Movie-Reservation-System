from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Movie, Genre, Showtime, Seat, Screen, Booked
from .serializers import MovieSerializer, GenreSerializer, ShowtimeSerializer, SeatSerializer, ScreenSerializer, BookedSerializer
from accounts.permissions import IsAdmin
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from accounts.models import User
from collections import defaultdict
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import datetime

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
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['genre']
    ordering_fields = ['title', 'duration']
    search_fields = ['title', 'description']
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
        movie = self.request.query_params.get('movie')
        screen = self.request.query_params.get('screen')
        if date:
            queryset = queryset.filter(show_date=date)
        if movie:
            queryset = queryset.filter(movie_id=movie)
        if screen:
            queryset = queryset.filter(screen_id=screen)
        return queryset
    # def validate_showtime(self, data):
    #     existing = Showtime.objects.filter(
    #         screen=data['screen'],
    #         show_date=data['show_date']
    #     )
    #     for show in existing:
    #         if (data['start_time'] < show.end_time and data['end_time'] > show.start_time):
    #             raise serializers.ValidationError("Showtime overlaps with existing showtime")
    #     return data
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
        if not showtime_id or not seat_id:
            return Response({"error": "Showtime and Seat are required"}, status=400)
        try:
            seat = Seat.objects.get(id=seat_id)
        except Seat.DoesNotExist:
            return Response({"error":"Seat Does not exist"},status=404)
        if Booked.objects.filter(showtime_id=showtime_id, seat_id=seat_id,status='BOOKED').exists():
            return Response({"error": "Seat Already Booked"}, status=400)
        showtime = get_object_or_404(Showtime,id=showtime_id)
        current_date = timezone.localdate()
        current_time = timezone.localtime().time()
        if seat.screen != showtime.screen:
            return Response({"error":"Seat does not belong to this screen"},status=400)
        if showtime.show_date < current_date or (showtime.show_date == current_date and showtime.start_time <= current_time):
            return Response({"error": "Cannot book past showtimes"}, status=400)
        try:
            booked = Booked.objects.create(
            user=request.user,
            showtime_id=showtime_id,
            seat_id=seat_id,
        )
        except IntegrityError:
            return Response({"error":"Seat Already Booked"},status=400)
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
        return Booked.objects.filter(user=self.request.user).select_related('showtime','showtime__movie','seat').order_by('-reserved_at')
    
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, booking_id):
        booking = get_object_or_404(Booked, id=booking_id, user=request.user)
        showtime = booking.showtime
        current_date = timezone.localdate()
        current_time = timezone.localtime().time()
        if (showtime.show_date < current_date or showtime.show_date == current_date and showtime.start_time <= current_time):
            return Response({"error":"Cannot cancel completed show"})
        else:
            if booking.status == 'CANCELLED':
                return Response({"error":"Booking already cancelled"},status=400)
            booking.save()
            return Response({"message": "Booking Cancelled Successfully"})
    
class AdminReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        total_bookings = Booked.objects.count()
        active_bookings = Booked.objects.filter(status='BOOKED').count()
        cancelled_bookings = Booked.objects.filter(status='CANCELLED').count()
        booked_tickets = Booked.objects.filter(status='BOOKED')
        revenue = sum(
            booking.showtime.ticket_price 
            for booking in booked_tickets            
        )
        
        return Response({
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": revenue
        })
    
class DashboardStatsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        total_movies = Movie.objects.count()
        total_showtimes = Showtime.objects.count()
        total_bookings = Booked.objects.filter(status='BOOKED').count()
        total_users = User.objects.count()
        revenue = 0
        bookings = Booked.objects.filter(status='BOOKED').select_related('showtime')
        for booking in bookings:
            revenue += booking.showtime.ticket_price
        return Response({
            "total_movies": total_movies,
            "total_showtimes": total_showtimes,
            "total_bookings": total_bookings,
            "total_users": total_users,
            "total_revenue": revenue
        })
    
class RevenueByMovieView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        data = defaultdict(lambda:{
            "bookings":0,
            "revenue":0
        })
        bookings = Booked.objects.filter(status='BOOKED').select_related('showtime__movie')
        for booking in bookings:
            movie = booking.showtime.movie.title
            data[movie]["bookings"] += 1
            data[movie]["revenue"] += float(booking.showtime.ticket_price)
        result = []
        for movie, values in data.items():
            result.append({
                "movie": movie,
                "bookings": values["bookings"],
                "revenue": values["revenue"]
            })
        return Response(result)
    
class OccupancyReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        report = []
        showtimes = Showtime.objects.select_related('movie', 'screen')
        for showtime in showtimes:
            total_seats = Seat.objects.filter(screen=showtime.screen).count()
            booked_seats = Booked.objects.filter(showtime=showtime, status='BOOKED').count()
            occupancy = 0
            if total_seats > 0:
                occupancy = round((booked_seats / total_seats) * 100,2)
            report.append({
                "showtime_id": showtime.id,
                "movie": showtime.movie.title,
                "screen": showtime.screen.name,
                "total_seats": total_seats,
                "booked_seats": booked_seats,
                "occupancy_percentage": occupancy
            })
        return Response(report)
    
class TopMoviesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        top_movies = Booked.objects.filter(status='BOOKED').values('showtime__movie__title').annotate(total_bookings=Count('id')).order_by('-total_bookings')
        result = []
        for movie in top_movies:
            result.append({
                "movie": movie['showtime__movie__title'],
                "bookings": movie['total_bookings']
            })
        return Response(result)