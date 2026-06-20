from rest_framework import serializers
from .models import Booked, Genre, Movie, Screen, Seat, Showtime

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    poster = serializers.ImageField(required=False)
    def validate_poster(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image too Large")
            if not value.content_type.startswith('image'):
                raise serializers.ValidationError("Invalid Image")
        return value
    
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
    def validate(self, data):
        # print("Validation is running")
        screen = data.get('screen')
        show_date = data.get('show_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be later than start time")
        existing_showtimes = Showtime.objects.filter(screen=screen, show_date=show_date)
        if self.instance:
            existing_showtimes = existing_showtimes.exclude(id=self.instance.id)
        for show in existing_showtimes:
            if (start_time < show.end_time and end_time > show.start_time):
                raise serializers.ValidationError("Showtime overlaps with existing showtime")
        return data
    
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
        
class MovieDetailSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(
        source = 'genre.name',
        read_only = True
    )
    class Meta:
        model = Movie
        fields = '__all__'