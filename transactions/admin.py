from django.contrib import admin

# Register your models here.

from .models import CategoryGroup, Category, TransactionType, Transaction

admin.site.register(CategoryGroup)
admin.site.register(Category)
admin.site.register(TransactionType)
admin.site.register(Transaction)