from django.db import models

# Create your models here.

class Bank(models.Model):
    name = models.CharField(max_length=200)
    hide = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Currency(models.Model):
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "currencies"

class Account(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.bank.name + '; ' + self.number + '; ' + self.name

    def has_account_number(self):
        return self.number != ''

