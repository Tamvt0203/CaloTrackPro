from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self.create_user(username, password=password, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    GENDER_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male')
    ]

    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    dateofbirth = models.DateField(default=timezone.now)
    currentweight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='Female')
    recommendcalo = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class WeightHistory(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.IntegerField()

class Food(models.Model):
    foodid = models.AutoField(primary_key=True)
    foodname = models.CharField(max_length=255)
    foodunit = models.CharField(max_length=50)
    foodcalo = models.IntegerField()

class FoodUser(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ]
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    foodid = models.ForeignKey(Food, on_delete=models.CASCADE)
    meal = models.CharField(max_length=10, choices=MEAL_CHOICES)
    quantity = models.IntegerField()
    foodtotalcalo = models.IntegerField()

class CaloHistory(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    datetotalcalo = models.IntegerField()


