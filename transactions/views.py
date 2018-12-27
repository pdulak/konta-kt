from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncMonth, TruncYear

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
        .order_by('month')

    context = {
        'months_list': months_list,
    }
    return render(request, 'transactions/monthly_review.html', context)
