from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from movies.models import *

User = get_user_model()


class ReportTests(APITestCase):

    def setUp(self):

        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            role="Admin"
        )

        self.genre = Genre.objects.create(
            name="Action"
        )

        self.movie = Movie.objects.create(
            title="Interstellar",
            description="Sci-Fi",
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

        self.showtime = Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            show_date="2030-01-01",
            start_time="18:00:00",
            end_time="21:00:00",
            ticket_price=250
        )

        self.user = User.objects.create_user(
            username="user1",
            password="user123",
            role="User"
        )

        Booked.objects.create(
            user=self.user,
            showtime=self.showtime,
            seat=self.seat,
            status="BOOKED"
        )

        self.client.force_authenticate(self.admin)

    def test_admin_report(self):

        response = self.client.get(
            "/api/reports/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "total_bookings",
            response.data
        )

    def test_dashboard_stats(self):

        response = self.client.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "total_movies",
            response.data
        )

    def test_revenue_by_movie(self):

        response = self.client.get(
            "/api/reports/revenue-by-movie/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_occupancy_report(self):

        response = self.client.get(
            "/api/reports/occupancy/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_top_movies_report(self):

        response = self.client.get(
            "/api/reports/top-movies/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )