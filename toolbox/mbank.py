import os
import re
import glob
import pandas as pd
from io import StringIO

from django.conf import settings
from loguru import logger

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


def trim_text_fields(x):
    return ' '.join(str(x).split())


def load_csv():
    # load all csv files from temp dir
    source_dir = os.path.join(settings.BASE_DIR, 'temp')
    field_names = ['Date', 'Added', 'Type', 'Description', 'Party Name', 'Party IBAN', 'Amount', 'Balance',
                   'Account Number']
    df = pd.DataFrame()

    list_of_files = glob.glob(os.path.join(source_dir, '*.csv'))
    for this_file in list_of_files:
        logger.info("adding {}".format(this_file))
        this_account_number = ''
        this_data = ''
        save_account_number = False
        save_transactions = False
        with open(this_file, encoding='cp1250') as f:
            for line in f:
                if line[:15] == '#Numer rachunku':
                    save_account_number = True
                elif line[:14][:9] == '#Data ksi':
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

        df_temp = pd.read_csv(StringIO(this_data), sep=';', comment='#', engine='python', names=field_names,
                              quotechar='|', encoding='cp1250', dtype={'Party IBAN': 'str'})

        logger.warning(this_file);
        logger.warning(this_data);
        logger.warning(this_account_number);
        # logger.info(df_temp);

        df_temp['Account Number'] = this_account_number
        df_temp['Source'] = os.path.basename(this_file)
        df_temp['Description'] = df_temp['Description'].fillna('')
        df_temp['Party IBAN'] = df_temp['Party IBAN'].fillna('')
        df_temp['Party Name'] = df_temp['Party Name'].fillna('')
        df_temp['Type'] = df_temp['Type'].fillna('')

        df_temp['Date Modified'] = df_temp['Description'].map(extract_date_from_description)
        df_temp['Description'] = df_temp['Description'].map(trim_text_fields)
        df_temp['Party Name'] = df_temp['Party Name'].map(trim_text_fields)
        df_temp['Type'] = df_temp['Type'].map(trim_text_fields)

        df_temp['Date Modified'] = df_temp['Date Modified'].fillna(df_temp['Date'])
        df_temp['Amount Modified'] = df_temp['Amount'].map(
            lambda x: float(re.sub('[^0-9\,\.-]','', x).replace(',', '.')))
        df_temp['Balance Modified'] = df_temp['Balance'].map(
            lambda x: float(re.sub('[^0-9\,\.-]', '', x).replace(',', '.')))

        df = df.append(df_temp, ignore_index=True)
        logger.info("added {}".format(df_temp.shape))

    logger.info("whole DF shape: {}".format(df.shape))
    logger.info(df.info())

    return df
