from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from transactions.views import get_account_balance, get_monthly_review, get_transactions_review


def index(request):
    context = {
        'accounts_list': get_account_balance(),
        'months_list': get_monthly_review()[:3],
    }
    return render(request, 'dashboard/dashboard.html', context)


def j_transactions(request):
    transactions_query, filter_start_date, filter_end_date = get_transactions_review(irrelevant=request.POST.get('irrelevant'),
                                                          account_id=request.POST.get('account'),
                                                          direction=request.POST.get('direction'),
                                                          startDate=request.POST.get('startDate'),
                                                          endDate=request.POST.get('endDate'),
                                                          sortOrder=request.POST.get('sortOrder'))
    data = {
        'transactions_list': list(transactions_query),
        'startDate': filter_start_date,
        'endDate': filter_end_date
    }
    return JsonResponse(data)
