from django.db import models

# Create your models here.

class CategoryGroup(models.Model):
    group_name = models.CharField(max_length=100)
    income = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name

class Category(models.Model):
    category_group = models.ForeignKey(CategoryGroup, on_delete=models.PROTECT, null=True, blank=True)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "categories"

class TransactionType(models.Model):
    type_name = models.CharField(max_length=200)

    def __str__(self):
        return self.type_name

class Transaction(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT)
    type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    uuid_text = models.CharField(max_length=200)
    transaction_date = models.DateField()
    transaction_added = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_description = models.CharField(max_length=2000)
    transaction_imported_description = models.CharField(max_length=2000)
    party_name = models.CharField(max_length=500)
    party_IBAN = models.CharField(max_length=200)
    irrelevant = models.BooleanField(default=False)
