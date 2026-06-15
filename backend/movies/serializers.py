from rest_framework import serializers
from .models import Booked, Genre, Movie, Screen, Seat, Showtime

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    class Meta:
        model = Movie
        fields = [
            'id',
            'title',
            'description',
            'duration',
            'genre',
            'genre_name',
            'poster'
        ]

class ShowtimeSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    screen_name = serializers.CharField(source='screen.name', read_only=True)
    class Meta:
        model = Showtime
        fields = [
            'id',
            'movie',
            'movie_title',
            'screen',
            'screen_name',
            'show_date',
            'start_time',
            'end_time',
            'ticket_price'
        ]

class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    seat_label = serializers.SerializerMethodField()
    class Meta:
        model = Seat
        fields = [
            'id',
            'screen',
            'row',
            'number',
            'seat_label'
        ]
    def get_seat_label(self, obj):
        return f"{obj.row}{obj.number}"
    
class BookedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='showtime.movie.title', read_only=True)
    class Meta:
        model = Booked
        fields = [
            'id',
            'user',
            'username',
            'showtime',
            'movie_title',
            'seat',
            'status',
            'reserved_at'
        ]
        read_only_fields = [
            'user',
            'status',
            'reserved_at']