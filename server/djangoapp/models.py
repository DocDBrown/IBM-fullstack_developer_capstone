# Uncomment the following imports before adding the Model code
from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

class CarMake(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    SUV = 'SUV'
    Sedan = 'Sedan'
    Wagon = 'Wagon'
    car_choice = [
        (SUV, 'SUV'),
        (Sedan, 'Sedan'),
        (Wagon, 'Wagon'),
    ]
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=10, choices=car_choice, default='SUV')
    year = models.IntegerField(default=2023, 
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ])

    def __str__(self):
        return self.name  

