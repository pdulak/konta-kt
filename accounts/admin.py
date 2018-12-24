from django.contrib import admin

# Register your models here.

from .models import Account, Bank, Currency

admin.site.register(Bank)
admin.site.register(Account)
admin.site.register(Currency)