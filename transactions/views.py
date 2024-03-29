from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.db.models import Sum, Q, DecimalField
from django.db.models.functions import TruncMonth, Cast
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Transaction
from accounts.models import Account, Currency
from loguru import logger
from toolbox import nbp


def chk_date(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False


def get_account_balance():
    return Transaction.objects \
        .select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .values('account', 'account__name', 'account__bank__name', 'account__bank__id', 'account__bank__hide',
                'account__currency__name', 'account__id') \
        .annotate(
            total=Sum('amount_account_currency'),
            down=Sum('amount_account_currency', filter=Q(amount_account_currency__lt=0)),
            up=Sum('amount_account_currency', filter=Q(amount_account_currency__gt=0)),
        ) \
        .annotate(
            ttotal=Cast('total', DecimalField(max_digits=14, decimal_places=2)),
        ) \
        .order_by('account__bank__hide', 'account__bank__name', 'account__name', 'account')


def get_monthly_review():
    return Transaction.objects.filter(irrelevant=False)\
        .values(month=TruncMonth('date'))\
        .annotate(
            total=Sum('amount'),
            down=Sum('amount', filter=Q(amount__lt=0)),
            up=Sum('amount', filter=Q(amount__gt=0)),
        )\
        .order_by('-month')


@login_required(login_url='/auth/login/')
def change_relevancy(request):
    t_id = request.POST.get('t_id')
    r_to_set = (request.POST.get('r_to_set') == 'true')

    Transaction.objects.filter(id=t_id).update(irrelevant=r_to_set)

    data = {
        'r_set': r_to_set
    }
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
def change_approval(request):
    t_id = request.POST.get('t_id')
    a_to_set = (request.POST.get('a_to_set') == 'true')

    Transaction.objects.filter(id=t_id).update(approved=a_to_set)

    data = {
        'a_set': a_to_set
    }
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
def save(request):
    t_id = request.POST.get('tr_id')

    this_account = Account.objects.get(id=request.POST.get('tr_account'))

    if int(t_id):
        logger.info('Updating existing transaction {}'.format(t_id))
        this_tr = Transaction.objects.filter(id=t_id).update(
            account=this_account,
            date=request.POST.get('tr_date'),
            amount=request.POST.get('tr_amount'),
            amount_account_currency=request.POST.get('tr_amount'),
            currency_multiplier=1,
            description=request.POST.get('tr_description'),
            irrelevant=(request.POST.get('tr_irrelevant') == 'true')
        )
        data = {
            't': t_id
        }
    else:
        # new transaction
        this_tr = Transaction.objects.create(
            account=this_account,
            date=request.POST.get('tr_date'),
            added=date.today(),
            amount=request.POST.get('tr_amount'),
            balance=0,
            amount_account_currency=request.POST.get('tr_amount'),
            balance_account_currency=0,
            currency_multiplier=1,
            description=request.POST.get('tr_description'),
            imported_description=request.POST.get('tr_description'),
            type='Added manually',
            irrelevant=(request.POST.get('tr_irrelevant') == 'true')
        )
        data = {
            't': this_tr.id
        }

    if this_account.currency.name == 'PLN':
        nbp.adjust_pln_transaction_rate(data['t'])
    else:
        nbp.adjust_non_pln_transaction_rate(data['t'], this_account.currency.name)

    return JsonResponse(data)


def get_transactions_review(irrelevant, account_id, direction, start_date,
                            end_date, sort_order):
    t = Transaction.objects

    # relevancy filter
    if irrelevant[0] == 'T':
        t = t.filter(irrelevant=1)
    elif irrelevant[0] == 'F':
        t = t.filter(irrelevant=0)

    # account filter
    if account_id[0].isdigit():
        t = t.filter(account__id=account_id[0])

    # direction filter
    if direction[0] == 'I':
        t = t.filter(amount_account_currency__gte=0)
    elif direction[0] == 'O':
        t = t.filter(amount_account_currency__lte=0)

    # check date fields, set minimum and maximum date properly
    if chk_date(start_date[0]):
        filter_start_date = datetime.strptime(start_date[0], "%Y-%m-%d")
    else:
        d = date.today() - relativedelta(months=1)
        filter_start_date = date(d.year, d.month, 1)

    if chk_date(end_date[0]):
        filter_end_date = datetime.strptime(end_date[0], "%Y-%m-%d")
    else:
        filter_end_date = date.today()

    t = t.filter(date__gte=filter_start_date).filter(date__lte=filter_end_date)

    ordering = ['-date', 'irrelevant', '-id']
    if sort_order[0] == 'date':
        ordering = ['date', 'irrelevant', '-id']
    elif sort_order[0] == 'amount':
        ordering = ['amount', '-date', 'irrelevant', '-id']
    elif sort_order[0] == '-amount':
        ordering = ['-amount', '-date', 'irrelevant', '-id']

    # the query itself
    t = t.select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .select_related('category') \
        .values('account', 'account__name', 'amount_account_currency', 'date', 'description', 'party_name',
                'account__currency__name', 'approved', 'amount',
                'category__name', 'category__id', 'type', 'account__bank__name', 'irrelevant', 'id', 'account__id') \
        .order_by(*ordering)

    return t, filter_start_date.strftime('%Y-%m-%d'), filter_end_date.strftime('%Y-%m-%d')


@login_required(login_url='/auth/login/')
def monthly_review(request):
    context = {
        'months_list': get_monthly_review(),
    }
    return render(request, 'transactions/monthly_review.html', context)


@login_required(login_url='/auth/login/')
def account_balance(request):
    context = {
        'accounts_list': get_account_balance(),
    }
    return render(request, 'transactions/account_balance.html', context)


@login_required(login_url='/auth/login/')
def months(request):
    data = {
        'months': list(get_monthly_review()[:3])
    }
    return JsonResponse(data)
