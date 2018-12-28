from django.db import models
from toolbox.models import ImportHeader


class CategoryGroup(models.Model):
    name = models.CharField(max_length=100)
    income = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Category(models.Model):
    group = models.ForeignKey(CategoryGroup, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class TransactionType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    import_header = models.ForeignKey(ImportHeader, on_delete=models.PROTECT, blank=True, null=True)
    uuid_text = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField()
    added = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_account_currency = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_account_currency = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency_multiplier = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    description = models.CharField(max_length=2000, blank=True, null=True)
    imported_description = models.CharField(max_length=2000, blank=True, null=True)
    type = models.CharField(max_length=2000, blank=True, null=True)
    party_name = models.CharField(max_length=500, blank=True, null=True)
    party_IBAN = models.CharField(max_length=200, blank=True, null=True)
    irrelevant = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.description + '; ' + self.imported_description + '; ' + str(self.date) + '; ' + str(self.amount) + ' PLN; ' + str(self.amount_account_currency) + ' ' + str(self.account.currency.name)


class TransactionImportTemp(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT)
    import_header = models.ForeignKey(ImportHeader, on_delete=models.PROTECT, blank=True, null=True)
    uuid_text = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField()
    added = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_account_currency = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_account_currency = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency_multiplier = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    imported_description = models.CharField(max_length=2000, blank=True, null=True)
    type = models.CharField(max_length=2000, blank=True, null=True)
    party_name = models.CharField(max_length=500, blank=True, null=True)
    party_IBAN = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.imported_description + '; ' + str(self.date) + '; ' + str(self.amount) + ' PLN; ' + str(self.amount_account_currency) + ' ' + str(self.account.currency.name)
