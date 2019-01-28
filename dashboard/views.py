from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from transactions.views import get_account_balance, get_monthly_review, get_transactions_review


def index(request):
    context = {
        'accounts_list': get_account_balance(),
        'months_list': get_monthly_review()[:5],
    }
    return render(request, 'dashboard/dashboard.html', context)


def j_transactions(request):
    data = {
        'transactions_list': list(get_transactions_review(irrelevant=request.POST.get('irrelevant'),
                                                          account_id=request.POST.get('account'),
                                                          direction=request.POST.get('direction'))[:500]),
    }
    return JsonResponse(data)
