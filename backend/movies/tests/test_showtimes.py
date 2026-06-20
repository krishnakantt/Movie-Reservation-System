from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from movies.models import *

User = get_user_model()

class ShowtimeTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            role="Admin"
        )
        self.genre = Genre.objects.create(name="Action")
        self.movie = Movie.objects.create(
            title= "Voyeor",
            description= "Romance",
            duration=170,
            genre= self.genre
        )
        self.screen = Screen.objects.create(
            name="Screen 1",
            capacity=100
        )
        self.client.force_authenticate(self.admin)
        Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            show_date="2026-06-20",
            start_time="18:00:00",
            end_time="20:00:00",
            ticket_price=250
        )
        response = self.client.post(
            "/api/showtimes/",
            {
                "movie":self.movie.id,
                "screen":self.screen.id,
                "show_date":"2026-06-20",
                "start_time":"19:00:00",
                "end_time":"21:00:00",
                "ticket_price":250
            }
        )
        self.assertEqual(response.status_code, 400)