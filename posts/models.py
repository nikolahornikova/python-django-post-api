from django.db import models


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False)
    external_id = models.IntegerField(null=True, unique=True)
    title = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)
