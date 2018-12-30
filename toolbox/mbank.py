import os
import re
import glob
import pandas as pd
import datetime

from django.conf import settings

from .models import ImportHeader
from accounts.models import Account
from transactions.models import TransactionType, Transaction, TransactionImportTemp

description_split_text = 'DATA TRANSAKCJI:'


def extract_date_from_description(x):
    parts = re.split(description_split_text, x)
    if len(parts) > 1:
        return parts[1].strip()

    return None


def trim_description(x):
    parts = re.split(description_split_text, x)
    if len(parts) > 1:
        return parts[0].strip()

    return x


def load_csv():
    # load all csv files from temp dir
    sourceDir = os.path.join(settings.BASE_DIR, 'temp')
    field_names = ['Date', 'Added', 'Type', 'Description', 'Party Name', 'Party IBAN', 'Amount', 'Balance',
                   'Account Number']
    df = pd.DataFrame()

    first_one = re.compile(r'^"')
    last_one = re.compile(r'"$')

    list_of_files = glob.glob(os.path.join(sourceDir, '*.csv'))
    for this_file in list_of_files:
        print('adding: ', this_file)
        this_account_number = ''
        this_data = ''
        save_account_number = False
        save_transactions = False
        with open(this_file, encoding='cp1250') as f:
            for line in f:
                if line[:15] == '#Numer rachunku':
                    save_account_number = True
                elif line[:14] == '#Data operacji':
                    save_transactions = True
                elif save_account_number:
                    this_account_number = line[:32].replace(' ', '')
                    save_account_number = False
                elif save_transactions:
                    if line[0] == '2':
                        this_data += line.replace("'", '"').replace('";"', "|;|").\
                            replace('";', "|;").replace(';"', ";|")
                    else:
                        save_transactions = False

        df_temp = pd.read_csv(pd.compat.StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
                              quotechar='|', encoding='cp1250')

        df_temp['Account Number'] = this_account_number
        df_temp['Source'] = os.path.basename(this_file)
        df_temp['Description'] = df_temp['Description'].fillna('')
        df_temp['Party IBAN'] = df_temp['Party IBAN'].fillna('')
        df_temp['Date Modified'] = df_temp['Description'].map(extract_date_from_description)
        df_temp['Description'] = df_temp['Description'].map(trim_description)
        df_temp['Date Modified'] = df_temp['Date Modified'].fillna(df_temp['Date'])
        df_temp['Amount Modified'] = df_temp['Amount'].map(
            lambda x: float(re.sub('[^0-9\,\.-]','', x).replace(',', '.')))
        df_temp['Balance Modified'] = df_temp['Balance'].map(
            lambda x: float(re.sub('[^0-9\,\.-]', '', x).replace(',', '.')))

        df = df.append(df_temp, ignore_index=True)
        print('added: ', df_temp.shape)

    print("Whole dataframe shape: ", df.shape)
    print(df.info())
    # pd.set_option('display.max_columns', None)
    # print(df.sample(10))

    return df


def do_import(df):
    print('--------------------------------------------------------')
    numbered_accounts = Account.objects.exclude(number__isnull=True).exclude(number__exact='')
    accounts_numbers = {}
    import_headers = {}
    last_source = ''
    last_account = ''

    if numbered_accounts.count() > 0:
        # prepare dictionary of account numbers
        for a in numbered_accounts:
            accounts_numbers[a.number.replace(' ', '')] = a

        # do import
        for index, row in df.iterrows():
            if row['Account Number'] in accounts_numbers:
                if row['Source'] not in import_headers:
                    import_headers[row['Source']] = ImportHeader.objects.create(
                        source=row['Source'], date=datetime.datetime.now())

                if (last_source != row['Source']) | (last_account != row['Account Number']):
                    last_source = row['Source']
                    last_account = row['Account Number']
                    print(datetime.datetime.now(), ' importing ', last_account, '; ', last_source)

                this_transaction, created = TransactionImportTemp.objects.get_or_create(
                    account=accounts_numbers[row['Account Number']],
                    import_header=import_headers[row['Source']],
                    uuid_text=row['Date Modified']+"__"+str(row['Amount Modified']),
                    date=row['Date Modified'],
                    added=row['Added'],
                    amount=row['Amount Modified'],
                    balance=row['Balance Modified'],
                    amount_account_currency=row['Amount Modified'],
                    balance_account_currency=row['Balance Modified'],
                    currency_multiplier=1,
                    imported_description=row['Description'],
                    type=row['Type'],
                    party_name=row['Party Name'],
                    party_IBAN=row['Party IBAN']
                )
            else:
                print("Account number ", row['Account Number'], " not found")

        # copy from temp to main table

    else:
        print('Accounts with numbers not found')

    print('--------------------------------------------------------')
    print(datetime.datetime.now(), ' import finished')

    return True
