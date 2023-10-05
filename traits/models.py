from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=20)


# Create your models here.
