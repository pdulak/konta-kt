from django.db import models

# Create your models here.

class Bank(models.Model):
    bank_name = models.CharField(max_length=200)

    def __str__(self):
        return self.bank_name

class Currency(models.Model):
    currency_name = models.CharField(max_length=50)
    currency_abbr = models.CharField(max_length=10)

    def __str__(self):
        return self.currency_name

    class Meta:
        verbose_name_plural = "currencies"

class Account(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.account_name

    def has_account_number(self):
        return self.account_number != ''

