from django.db import models
from movies.models import Showtime, Seat
from accounts.models import User

# Create your models here.
class Reservation(models.Model):
    STATUS = (
        ('BOOKED','Booked'),
        ('CANCELLED','Cancelled'),
    )
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='BOOKED')
    created_at = models.DateTimeField(auto_now_add=True)

#ReservationSeat Model
class ReservationSeat(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('reservation', 'seat')
