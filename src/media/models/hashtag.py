from django.db import models


class Hashtag(models.Model):
    id = models.BigAutoField(primary_key=True)
    hashtag = models.CharField(max_length=100, unique=True)
    count = models.IntegerField(default=0)

    objects = models.Manager()
