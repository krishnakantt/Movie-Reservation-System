from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from movies.models import *

User = get_user_model()
class BookingsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            password="user123",
            role="User"
        )
        self.genre = Genre.objects.create(
            name="Action"
        )
        self.movie = Movie.objects.create(
            title = "Interstellar",
            description = "Sci-Fi Movie",
            duration=169,
            genre=self.genre
        )
        self.screen = Screen.objects.create(
            name="Screen 1",
            capacity=100
        )
        self.seat = Seat.objects.create(
            screen=self.screen,
            row="A",
            number=1
        )
        self.showtime=Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            show_date="2030-01-01",
            start_time="18:00:00",
            end_time="21:00:00",
            ticket_price=250
        )
        self.client.force_authenticate(self.user)
    
    def test_successful_booking(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "showtime": self.showtime.id,
                "seat": self.seat.id
            }
        )
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Booked.objects.count(),1)

    def test_duplicate_booking_fails(self):
        Booked.objects.create(
            user=self.user,
            showtime=self.showtime,
            seat=self.seat
        )
        response = self.client.post(
            "/api/bookings/",
            {
                "showtime":self.showtime.id,
                "seat":self.seat.id
            }
        )
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_available_seats(self):
        response =self.client.get(f"/api/showtimes/{self.showtime.id}/available-seats/")
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_cancel_booking(self):
        booking =Booked.objects.create(
            user =self.user,
            showtime=self.showtime,
            seat=self.seat
        )
        response = self.client.delete(
            f"/api/bookings/{booking.id}/cancel/"
        )
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status,"CANCELLED")

    def test_my_bookings(self):
        Booked.objects.create(
            user = self.user,
            showtime=self.showtime,
            seat=self.seat
        )
        response = self.client.get("/api/my-bookings/")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data["count"],1)