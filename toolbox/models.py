from django.db import models


class ImportHeader(models.Model):
    source = models.CharField(max_length=300)
    date = models.DateField()

    def __str__(self):
        return self.source + '; ' + str(self.date)
