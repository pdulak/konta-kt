from django.contrib import admin
from .models import Account, Bank, Currency

admin.site.register(Bank)
admin.site.register(Account)
admin.site.register(Currency)
