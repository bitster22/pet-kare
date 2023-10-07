from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)

# Create your models here.
