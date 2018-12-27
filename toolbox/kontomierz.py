import os
import re
import glob
import pandas as pd

from django.conf import settings

from accounts.models import Account, Bank, Currency
from transactions.models import CategoryGroup, Category, TransactionType, Transaction


def load_csv():
    # load all csv files from temp dir
    sourceDir = os.path.join(settings.BASE_DIR, 'temp')
    field_names = ['Bank', 'Nazwa konta', 'UID', 'DataTransakcji', 'DataKsiegowania', 'Kwota', 'Saldo',
                   'Opis', 'Tytul', 'Rodzaj', 'Strona', 'IBANStrony', 'Kategoria', 'Tagi', 'Nieistotna']
    df = pd.DataFrame()

    first_one = re.compile(r'^"')
    last_one = re.compile(r'"$')

    list_of_files = glob.glob(os.path.join(sourceDir, '*.csv'))
    for this_file in list_of_files:
        print('adding: ', this_file)
        this_data = ''
        with open(this_file, encoding='cp1250') as f:
            for line in f:
                temp_data = last_one.sub("|", line)
                temp_data = first_one.sub("|", temp_data)
                temp_data = temp_data.replace('";"', "|;|").replace('";', "|;").replace(';"', ";|")
                this_data += temp_data

        df_temp = pd.read_csv(pd.compat.StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
                              quotechar="|", encoding='cp1250')

        i = df_temp[(df_temp['IBANStrony'] == 'IBAN strony')].index
        df_temp = df_temp.drop(i)

        df = df.append(df_temp, ignore_index=True)
        print('added: ', df_temp.shape)

    print("Whole dataframe shape: ", df.shape)
    print(df.info())

    return df


def do_initial_load(df):
    already_inserted = []

    # print('Inserting Bank values')
    # for val, cnt in df['Bank'].value_counts().iteritems():
    #     if val not in already_inserted:
    #         obj, created = Bank.objects.get_or_create(
    #             name=val,
    #             defaults={},
    #         )
    #         already_inserted.append(val)

    already_inserted = []
    print('Inserting Kategoria values')
    for val, cnt in df['Kategoria'].value_counts().iteritems():
        if val not in already_inserted:
            obj, created = Category.objects.get_or_create(
                name=val,
                defaults={},
            )
            already_inserted.append(val)

    acc_bank = df.groupby(['Bank', 'Nazwa konta']).size().reset_index(name="Count")
    for index, row in acc_bank.iterrows():
        this_bank, created = Bank.objects.get_or_create(name=row['Bank'])
        this_account, created = Account.objects.get_or_create(bank=this_bank, name=row['Nazwa konta'])

    return True
