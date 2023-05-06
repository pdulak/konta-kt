# from . import kontomierz
from . import mbank
from . import alior
from . import common
from . import nbp
from datetime import datetime

# from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from accounts.models import Account, Bank, Currency
from transactions.models import CategoryGroup, Category, TransactionType, Transaction

from loguru import logger

from accounts.models import Account
from json2html import *

@login_required(login_url='/auth/login/')
def index(request):
    return HttpResponse("Hello, world. You're at the toolbox index.")


@login_required(login_url='/auth/login/')
def review_database(request):
    latest_accounts_list = Account.objects.order_by('-id')[:15]
    all_banks_list = Bank.objects.order_by('id')
    all_currencies_list = Currency.objects.order_by('id')
    all_category_groups_list = CategoryGroup.objects.order_by('id')
    all_categories_list = Category.objects.order_by('id')
    all_transaction_types_list = TransactionType.objects.order_by('id')
    all_transactions_list = Transaction.objects.order_by('-date')[:20]

    logger.info(all_transaction_types_list)
    logger.info(all_transactions_list)

    context = {
        'latest_accounts_list': latest_accounts_list,
        'all_banks_list': all_banks_list,
        'all_currencies_list': all_currencies_list,
        'all_category_groups_list': all_category_groups_list,
        'all_categories_list': all_categories_list,
        'all_transaction_types_list': all_transaction_types_list,
        'all_transactions_list': all_transactions_list,
    }

    logger.info(context)

    return render(request, 'toolbox/review.html', context)


@login_required(login_url='/auth/login/')
def load_kontomierz(request):
    # df = kontomierz.load_csv()
    #
    # # remove already insterted data
    # Transaction.objects.all().delete()
    # TransactionType.objects.all().delete()
    # Category.objects.all().delete()
    # CategoryGroup.objects.all().delete()
    # Account.objects.all().delete()
    # Bank.objects.all().delete()
    #
    # # import base data
    # kontomierz.do_initial_load(df)

    return HttpResponse("Loading kontomierz CSV;")


@login_required(login_url='/auth/login/')
def load_mbank(request):
    df = mbank.load_csv()
    df['import_source'] = 'CSV'
    df['Transaction ID'] = ''

    df_duplicates, df_imported = common.do_import(df)

    return HttpResponse(f"Imported: {df_imported.shape[0]}, Duplicates: {df_duplicates.shape[0]}")


@login_required(login_url='/auth/login/')
def load_alior(request):
    df = alior.load_csv()
    df['import_source'] = 'CSV'
    df['Transaction ID'] = ''

    df_duplicates, df_imported = common.do_import(df)

    return HttpResponse(f"Imported: {df_imported.shape[0]}, Duplicates: {df_duplicates.shape[0]}")


@login_required(login_url='/auth/login/')
def adjust_nbp(request):
    return HttpResponse("NBP tables review finished, reviewed {} NON-PLN transactions and {} PLN transactions".format(nbp.check_non_pln_transactions(), nbp.check_pln_transactions()))


@login_required(login_url='/auth/login/')
def do_cleanup(request):
    common.do_cleanup()

    return HttpResponse("Cleanup performed");


@login_required(login_url='/auth/login/')
def load_nordigen(request):
    context = {
        'accounts' : Account.objects.select_related('bank') \
        .exclude(nordigen_id__isnull=True) \
        .exclude(nordigen_id__exact='') \
        .values('name', 'bank__name', 'nordigen_id') \
        .order_by('bank__name', 'name')
    }

    return render(request, 'toolbox/load_nordigen.html', context)
