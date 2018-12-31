from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Sum, F, Q, DecimalField
from django.db.models.functions import TruncMonth, TruncYear, Cast

from .models import Transaction


def get_account_balance():
    return Transaction.objects \
        .select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .values('account', 'account__name', 'account__bank__name', 'account__bank__id', 'account__bank__hide',
                'account__currency__name') \
        .annotate(
            total=Sum('amount_account_currency'),
            down=Sum('amount_account_currency', filter=Q(amount_account_currency__lt=0)),
            up=Sum('amount_account_currency', filter=Q(amount_account_currency__gt=0)),
        ) \
        .annotate(
            ttotal=Cast('total', DecimalField(max_digits=14, decimal_places=2)),
        ) \
        .order_by('account__bank__hide', 'account__bank__name', 'account')


def get_monthly_review():
    return Transaction.objects.filter(irrelevant=False)\
        .values(month=TruncMonth('date'))\
        .annotate(
            total=Sum('amount'),
            down=Sum('amount', filter=Q(amount__lt=0)),
            up=Sum('amount', filter=Q(amount__gt=0)),
        )\
        .order_by('-month')


def get_transactions_review():
    return Transaction.objects \
        .select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .select_related('category') \
        .values('account', 'account__name', 'amount_account_currency', 'date', 'description', 'account__currency__name',
                'category__name', 'category__id', 'type', 'account__bank__name', 'irrelevant') \
        .order_by('-date')


def index(request):
    return HttpResponse("Hello, world. You're at the transactions index.")


def monthly_review(request):
    context = {
        'months_list': get_monthly_review(),
    }
    return render(request, 'transactions/monthly_review.html', context)


def account_balance(request):
    context = {
        'accounts_list': get_account_balance(),
    }
    return render(request, 'transactions/account_balance.html', context)


def transactions_review(request):
    context = {
        'transactions_list': get_transactions_review()[:100],
    }
    return render(request, 'transactions/transactions_review.html', context)
