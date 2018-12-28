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
    field_names = ['Date', 'Added', 'Type', 'Description', 'Party Name', 'Party IBAN', 'Amount', 'Balance']
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
                    this_account_number = line[:32]
                    save_account_number = False
                elif save_transactions:
                    if line[0] == '2':
                        this_data += line
                    else:
                        save_transactions = False


                # temp_data = last_one.sub("|", line)
                # temp_data = first_one.sub("|", temp_data)
                # temp_data = temp_data.replace('";"', "|;|").replace('";', "|;").replace(';"', ";|")
                # this_data += temp_data

        print('----------------------------------------')
        print(this_data)
        print('----------------------------------------')
        print(this_account_number)
        print('----------------------------------------')

        # df_temp = pd.read_csv(pd.compat.StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
        #                       quotechar="|", encoding='cp1250')
        #
        # i = df_temp[(df_temp['IBANStrony'] == 'IBAN strony')].index
        # df_temp = df_temp.drop(i)
        #
        # df = df.append(df_temp, ignore_index=True)
        # print('added: ', df_temp.shape)

    # print("Whole dataframe shape: ", df.shape)
    # print(df.info())

    return df
