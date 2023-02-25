from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from transactions.views import get_account_balance, get_monthly_review, get_transactions_review


@login_required(login_url='/auth/login/')
def index(request):
    context = {
        'accounts_list': get_account_balance(),
        'months_list': get_monthly_review()[:3],
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='/auth/login/')
def j_transactions(request):
    transactions_query, filter_start_date, filter_end_date = get_transactions_review(**request.POST)
    data = {
        'transactions_list': list(transactions_query),
        'start_date': filter_start_date,
        'end_date': filter_end_date
    }
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
def account_balance(request):
    context = {
        'accounts_list': get_account_balance(),
    }
    return render(request, 'dashboard/accounts_info.html', context)
