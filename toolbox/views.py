# from . import kontomierz
from . import mbank
from . import alior
from . import common
from . import nbp
from datetime import datetime

# from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from accounts.models import Account, Bank, Currency
from transactions.models import CategoryGroup, Category, TransactionType, Transaction

from loguru import logger


def index(request):
    return HttpResponse("Hello, world. You're at the toolbox index.")


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


def load_kontomierz(request):
    # df = kontomierz.load_csv()
    # print(df.head())
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


def load_mbank(request):
    df = mbank.load_csv()

    common.do_import(df)

    return HttpResponse("Loaded mBank CSV;")


def load_alior(request):
    df = alior.load_csv()

    common.do_import(df)

    return HttpResponse("Loaded Alior CSV;")


def adjust_nbp(request):
    return HttpResponse("NBP tables review finished, reviewed {} transactions".format(nbp.check_non_pln_transactions()))
