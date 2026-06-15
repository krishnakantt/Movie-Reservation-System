from django.db import models
from django.conf import settings

# Create your models here.
#Genre Model
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

#Movie Model
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.ImageField(
        upload_to = 'posters/',
        blank= True,
        null= True
    )
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    duration = models.IntegerField()

    def __str__(self):
        return self.title

#Screen Model
class Screen(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

#Seat Model
class Seat(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    row = models.CharField(max_length=5)
    number = models.IntegerField()
    def __str__(self):
        return f"{self.row}-{self.number}"
    
#Showtime Model
class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    show_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} at {self.start_time}"
    
#Booked Model
class Booked(models.Model):
    STATUS_CHOICES = (
        ('BOOKED', 'Booked'),
        ('CANCELLED', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BOOKED')
    class Meta:
        unique_together = ('showtime', 'seat')

    def __str__(self):
        return f"{self.user.username} - {self.showtime.movie.title}"