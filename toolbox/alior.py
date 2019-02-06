import os
import re
import glob
import pandas as pd
import datetime

from django.conf import settings

from .models import ImportHeader
from accounts.models import Account
from transactions.models import TransactionType, Transaction, TransactionImportTemp


def get_account_number(x):
    account_number = x['destinationIBAN']
    if x['Amount'] < 0:
        account_number = x['sourceIBAN']

    return account_number.replace(' ', '')


def get_party_iban(x):
    account_number = x['destinationIBAN']
    if x['Amount'] > 0:
        account_number = x['sourceIBAN']

    return account_number.replace(' ', '')


def get_party_name(x):
    party_name = x['Destination']
    if x['Amount'] > 0:
        party_name = x['Source Party']

    return party_name


def load_csv():
    # load all csv files from temp dir
    sourceDir = os.path.join(settings.BASE_DIR, 'temp', 'alior')
    field_names = ['Date', 'Added', 'Source Party', 'Destination', 'Description', 'Amount', 'Currency', 'AmountAccount',
                   'CurrencyAccount', 'sourceIBAN', 'destinationIBAN', 'none']
    df = pd.DataFrame()

    first_one = re.compile(r'^"')
    last_one = re.compile(r'"$')

    list_of_files = glob.glob(os.path.join(sourceDir, '*.csv'))
    list_of_files += glob.glob(os.path.join(sourceDir, '*.CSV'))

    for this_file in list_of_files:
        print('adding: ', this_file)
        this_data = ''
        save_transactions = False
        blik_regex = re.compile(r"\;Płatność BLIK\;([^\;]*)\;Płatność BLIK\;([^\;]*)\;", re.IGNORECASE)

        with open(this_file, encoding='cp1250') as f:
            for line in f:
                if line[:15] == 'Data transakcji':
                    save_transactions = True
                elif save_transactions:
                    line = blik_regex.sub(r"\;Płatność BLIK | \1 | \2 \;", line)
                    this_data += line

        df_temp = pd.read_csv(pd.compat.StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
                              encoding='cp1250', dtype={'Date': 'str', 'Added': 'str', 'sourceIBAN': 'str',
                                                        'destinationIBAN': 'str'})

        df_temp['Source'] = os.path.basename(this_file)
        df_temp['Description'] = df_temp['Description'].fillna('')
        df_temp['Type'] = 'Alior NA'

        df_temp['Party Name'] = df_temp.apply(get_party_name, axis=1)
        df_temp['Party Name'] = df_temp['Party Name'].fillna('')
        df_temp['Party IBAN'] = df_temp.apply(get_party_iban, axis=1)
        df_temp['Party IBAN'] = df_temp['Party IBAN'].fillna('')
        df_temp['Account Number'] = df_temp.apply(get_account_number, axis=1)
        df_temp['Account Number'] = df_temp['Account Number'].fillna('')
        df_temp['Date'] = df_temp['Date'].map(lambda x: '-'.join([x.split('-')[2], x.split('-')[1], x.split('-')[0]]))
        df_temp['Added'] = df_temp['Added'].map(lambda x: '-'.join([x.split('-')[2], x.split('-')[1], x.split('-')[0]]))

        df_temp['Date Modified'] = df_temp['Date']
        df_temp['Amount Modified'] = df_temp['Amount']
        df_temp['Balance Modified'] = 0

        df_temp = df_temp.drop(['CurrencyAccount', 'AmountAccount', 'none', 'Source Party', 'Destination',
                                'sourceIBAN', 'destinationIBAN', 'Currency'], axis=1)

        df = df.append(df_temp, ignore_index=True)
        print('added: ', df_temp.shape)

    print("Whole dataframe shape: ", df.shape)
    print(df.info())

    # print(df["Party IBAN"].value_counts())

    pd.set_option('display.max_columns', None)
    print(df.head(6))

    return df