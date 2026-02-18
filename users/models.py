from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=50, blank=True, unique=True)
    birth_data = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
