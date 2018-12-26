import os
import re
import glob
import pandas as pd

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from accounts.models import Account, Bank, Currency
from transactions.models import CategoryGroup, Category, TransactionType, Transaction

def index(request):
    return HttpResponse("Hello, world. You're at the toolbox index.")


def cleanup_database(request):
    return HttpResponse("Cleanup database")


def initialize_database(request):
    return HttpResponse("Initialize database")


def review_database(request):
    latest_accounts_list = Account.objects.order_by('-id')[:5]
    all_banks_list = Bank.objects.order_by('id')
    all_currencies_list = Currency.objects.order_by('id')
    all_categoryGroups_list = CategoryGroup.objects.order_by('id')
    all_categories_list = Category.objects.order_by('id')
    all_transactionTypes_list = TransactionType.objects.order_by('id')
    all_transactions_list = Transaction.objects.order_by('id')

    context = {
        'latest_accounts_list': latest_accounts_list,
        'all_banks_list': all_banks_list,
        'all_currencies_list': all_currencies_list,
        'all_categoryGroups_list': all_categoryGroups_list,
        'all_categories_list': all_categories_list,
        'all_transactionTypes_list': all_transactionTypes_list,
        'all_transactions_list': all_transactions_list,
    }
    return render(request, 'toolbox/review.html', context)


def load_kontomierz(request):
    # load all csv files from temp dir
    sourceDir = os.path.join(settings.BASE_DIR, 'temp')
    field_names = ['Bank','Nazwa konta','UID transakcji','Data transakcji','Data ksiêgowania','Kwota','Saldo','Opis','Tytu³','Rodzaj','Strona','IBAN strony','Kategoria','Tagi','Nieistotna']
    df = pd.DataFrame()

    first_one = re.compile(r'^"')
    last_one = re.compile(r'"$')

    this_data = ''
    list_of_files = glob.glob(os.path.join(sourceDir, '*.csv'))
    for this_file in list_of_files:
        print('adding: ', this_file)
        with open(this_file, encoding='cp1250') as f:
            for line in f:
                temp_data = last_one.sub("|", line)
                temp_data = first_one.sub("|", temp_data)
                temp_data = temp_data.replace('";"', "|;|").replace('";', "|;").replace(';"', ";|")
                this_data += temp_data

        df_temp = pd.read_csv(pd.compat.StringIO(this_data), sep=';', comment='#', engine='python', names=field_names, skiprows=10,
                              quotechar="|", encoding='cp1250')
        df = df.append(df_temp, ignore_index=True)
        print('added: ',  df_temp.shape)

    print("Whole dataframe shape: ", df.shape)
    print(df.info())

    # extract unique values to insert into the database
    

    return HttpResponse("Loading CSV;")
