from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Sum, F, Q, DecimalField
from django.db.models.functions import TruncMonth, TruncYear, Cast

from .models import Transaction


def index(request):
    return HttpResponse("Hello, world. You're at the transactions index.")


def monthly_review(request):
    months_list = Transaction.objects.filter(irrelevant=False)\
        .values(month=TruncMonth('date'))\
        .annotate(
            total=Sum('amount'),
            down=Sum('amount', filter=Q(amount__lt=0)),
            up=Sum('amount', filter=Q(amount__gt=0)),
        )\
        .order_by('-month')

    context = {
        'months_list': months_list,
    }
    return render(request, 'transactions/monthly_review.html', context)


def account_balance(request):
    accounts_list = Transaction.objects \
        .select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .values('account', 'account__name', 'account__bank__name', 'account__currency__name') \
        .annotate(
            total=Sum('amount'),
            down=Sum('amount', filter=Q(amount__lt=0)),
            up=Sum('amount', filter=Q(amount__gt=0)),
        ) \
        .annotate(
            ttotal=Cast('total', DecimalField(max_digits=14, decimal_places=2)),
        ) \
        .order_by('account')

    context = {
        'accounts_list': accounts_list,
    }
    return render(request, 'transactions/account_balance.html', context)

