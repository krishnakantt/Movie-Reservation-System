from django.urls import path
from .views import AdminReportView, AvailableSeatsView, BookedListCreateView, CancelBookingView, GenreListCreateView, MovieListCreateView, MovieDetailView, MyBookingsView, ShowtimeListCreateView, ScreenListCreateView, SeatListCreateView

urlpatterns = [
    path('genres/', GenreListCreateView.as_view(), name='genre-list-create'),
    path('movies/', MovieListCreateView.as_view(), name='movie-list-create'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('showtimes/', ShowtimeListCreateView.as_view(), name='showtime-list-create'),
    path('screens/', ScreenListCreateView.as_view(), name='screen-list-create'),
    path('seats/', SeatListCreateView.as_view(), name='seat-list-create'),
    path('bookings/', BookedListCreateView.as_view(), name='booking-list-create'),
    path('showtimes/<int:showtime_id>/available-seats/', AvailableSeatsView.as_view(), name='available-seats'),
    path('my-bookings/', MyBookingsView.as_view(), name='my-bookings'),
    path('bookings/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('reports/', AdminReportView.as_view(), name='admin-report')
]