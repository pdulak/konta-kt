from django.db import models

# Create your models here.

class Bank(models.Model):
    bank_name = models.CharField(max_length=200)

    def __str__(self):
        return self.bank_name

class Account(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)

    def __str__(self):
        return self.account_name

    def has_account_number(self):
        return self.account_number != ''

