from django.shortcuts import render
from django.http import JsonResponse

from transactions.views import get_account_balance, get_monthly_review, get_transactions_review


def index(request):
    context = {
        'accounts_list': get_account_balance(),
        'months_list': get_monthly_review()[:3],
    }
    return render(request, 'dashboard/dashboard.html', context)


def j_transactions(request):
    transactions_query, filter_start_date, filter_end_date = get_transactions_review(**request.POST)
    data = {
        'transactions_list': list(transactions_query),
        'start_date': filter_start_date,
        'end_date': filter_end_date
    }
    return JsonResponse(data)
