from django.db import models

class NordigenTokens(models.Model):
    access = models.CharField(max_length=2048)
    refresh = models.CharField(max_length=2048)
    date_created = models.DateTimeField(auto_now_add=True)
    access_expiration = models.DateTimeField()
    refresh_expiration = models.DateTimeField()

    def __str__(self):
        return '{} - {}'.format(self.date_created, self.access_expiration)
