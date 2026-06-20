from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from movies.models import Genre, Movie

User = get_user_model()

class MovieTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            role="Admin"
        )
        self.user = User.objects.create_user(
            username="user",
            password="123456",
            role="User"
        )
        self.genre = Genre.objects.create(name="Action")
    
    def test_movie_list_requires_authentication(self):
        response = self.client.get("/api/movies/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_movies(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_movie(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "title": "Voyeor",
            "description": "Romance",
            "duration":170,
            "genre": self.genre.id
        }
        response = self.client.post("/api/movies/",payload)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_user_cannot_create_movie(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "Voyeor",
            "description": "Romance",
            "duration":170,
            "genre": self.genre.id
        }
        response = self.client.post("/api/movies/",payload)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        