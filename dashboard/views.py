from django.shortcuts import render
from django.http import HttpResponse

from transactions.views import get_account_balance, get_monthly_review


def index(request):
    context = {
        'accounts_list': get_account_balance(),
        'months_list': get_monthly_review()[:5]
    }
    return render(request, 'dashboard/dashboard.html', context)
