import os
import re
import glob
import pandas as pd
from io import StringIO

from django.conf import settings
from loguru import logger

def get_account_number(x):
    account_number = '76249000050000400031886744'
    if (float(x['Amount']) > 0) and (len(str(x['destinationIBAN'])) > 20):
        account_number = x['destinationIBAN']
    if (float(x['Amount']) < 0) and (len(str(x['sourceIBAN'])) > 20):
        account_number = x['sourceIBAN']

    return account_number.replace(' ', '')


def get_party_iban(x):
    account_number = str(x['destinationIBAN'])
    if float(x['Amount']) > 0:
        account_number = str(x['sourceIBAN'])

    return account_number.replace(' ', '')


def get_party_name(x):
    if float(x['Amount']) > 0:
        return x['Source Party']

    return x['Destination']


def load_csv():
    # load all csv files from temp dir
    source_dir = os.path.join(settings.BASE_DIR, 'temp', 'alior')
    field_names = ['Date', 'Added', 'Source Party', 'Destination', 'Description', 'Amount', 'Currency', 'AmountAccount',
                   'CurrencyAccount', 'sourceIBAN', 'destinationIBAN', 'none']
    df = pd.DataFrame()

    list_of_files = glob.glob(os.path.join(source_dir, '*.csv'))
    list_of_files += glob.glob(os.path.join(source_dir, '*.CSV'))

    for this_file in list_of_files:
        logger.info("adding {}".format(this_file))
        this_data = ''
        save_transactions = False
        blik_regex = re.compile(r"\;Płatność BLIK\;([^\;]*)\;Płatność BLIK\;([^\;]*)\;", re.IGNORECASE)

        with open(this_file, encoding='cp1250') as f:
            for line in f:
                if line[:15] == 'Data transakcji':
                    save_transactions = True
                elif save_transactions:
                    line = blik_regex.sub(r"\;Płatność BLIK | \1 | \2 \;", line)
                    line = line.replace("\"SALAD STORY\"","SALAD STORY")
                    this_data += line

        df_temp = pd.read_csv(StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
                              encoding='cp1250', dtype={'Date': 'str', 'Added': 'str', 'sourceIBAN': 'str',
                                                        'destinationIBAN': 'str'})

        df_temp['Source'] = os.path.basename(this_file)
        df_temp['Description'] = df_temp['Description'].fillna('')
        df_temp['Type'] = 'Alior NA'

        df_temp['Amount'] = df_temp['Amount'].map(lambda x: x.replace(",", "."))
        df_temp['Party Name'] = df_temp.apply(get_party_name, axis=1)
        df_temp['Party Name'] = df_temp['Party Name'].fillna('')
        df_temp['Party IBAN'] = df_temp.apply(get_party_iban, axis=1)
        df_temp['Party IBAN'] = df_temp['Party IBAN'].fillna('')
        df_temp['Account Number'] = df_temp.apply(get_account_number, axis=1)
        df_temp['Account Number'] = df_temp['Account Number'].fillna('76249000050000400031886744')
        df_temp['Date'] = df_temp['Date'].map(lambda x: '-'.join([x.split('-')[2], x.split('-')[1], x.split('-')[0]]))
        df_temp['Added'] = df_temp['Added'].map(lambda x: '-'.join([x.split('-')[2], x.split('-')[1], x.split('-')[0]]))

        df_temp['Date Modified'] = df_temp['Date']
        df_temp['Amount Modified'] = df_temp['Amount']
        df_temp['Balance Modified'] = 0

        df_temp = df_temp.drop(['CurrencyAccount', 'AmountAccount', 'none', 'Source Party', 'Destination',
                                'sourceIBAN', 'destinationIBAN', 'Currency'], axis=1)

        df = df.append(df_temp, ignore_index=True)
        logger.info("added {}".format(df_temp.shape))

    logger.info("whole DF shape: {}".format(df.shape))
    logger.info(df.info())

    return df
