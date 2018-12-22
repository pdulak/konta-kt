from django.contrib import admin

# Register your models here.

from .models import Bank
from .models import Account

admin.site.register(Bank)
admin.site.register(Account)