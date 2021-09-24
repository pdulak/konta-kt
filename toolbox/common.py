import glob
import os
import datetime
import shutil

from loguru import logger
from .models import ImportHeader
from django.conf import settings
from accounts.models import Account
from transactions.models import Transaction, TransactionImportTemp


def do_import(df):
    numbered_accounts = Account.objects.exclude(number__isnull=True).exclude(number__exact='')
    accounts_numbers = {}
    import_headers = {}
    last_source = ''
    last_account = ''

    if numbered_accounts.count():
        # prepare dictionary of account numbers
        for a in numbered_accounts:
            accounts_numbers[a.number.replace(' ', '')] = a

        # do import
        for index, row in df.iterrows():
            if row['Account Number'] in accounts_numbers:
                if row['Source'] not in import_headers:
                    import_headers[row['Source']] = ImportHeader.objects.create(
                        source=row['Source'], date=datetime.datetime.now())

                if (last_source != row['Source']) or (last_account != row['Account Number']):
                    last_source = row['Source']
                    last_account = row['Account Number']
                    logger.info("importing {} for account {}".format(last_source, last_account))

                # check for transaction duplicate
                is_duplicate = False

                chk_transaction = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                             account=accounts_numbers[row['Account Number']],
                                                             amount_account_currency=row['Amount Modified'],
                                                             balance_account_currency=row['Balance Modified'],
                                                             imported_description__contains=row['Description']
                                                             )\
                    .exclude(import_header=import_headers[row['Source']])\
                    .count()

                if chk_transaction:
                    is_duplicate = True
                else:
                    # insert if not duplicate
                    Transaction.objects.create(
                        account=accounts_numbers[row['Account Number']],
                        import_header=import_headers[row['Source']],
                        uuid_text=row['Date Modified'][:10] + "__" + str(row['Amount Modified']),
                        date=row['Date Modified'][:10],
                        added=row['Added'][:10],
                        amount=row['Amount Modified'],
                        balance=row['Balance Modified'],
                        amount_account_currency=row['Amount Modified'],
                        balance_account_currency=row['Balance Modified'],
                        currency_multiplier=1,
                        description=row['Description'],
                        imported_description=row['Description'],
                        type=row['Type'],
                        party_name=row['Party Name'],
                        party_IBAN=row['Party IBAN']
                    )

                # insert into import temp
                TransactionImportTemp.objects.create(
                    account=accounts_numbers[row['Account Number']],
                    import_header=import_headers[row['Source']],
                    uuid_text=row['Date Modified'][:10]+"__"+str(row['Amount Modified']),
                    date=row['Date Modified'][:10],
                    added=row['Added'][:10],
                    amount=row['Amount Modified'],
                    balance=row['Balance Modified'],
                    amount_account_currency=row['Amount Modified'],
                    balance_account_currency=row['Balance Modified'],
                    currency_multiplier=1,
                    imported_description=row['Description'],
                    type=row['Type'],
                    party_name=row['Party Name'],
                    party_IBAN=row['Party IBAN'],
                    is_duplicate=is_duplicate
                )
            else:
                logger.warning("Account number {} not found".format(row['Account Number']))

    else:
        logger.warning("Accounts with numbers not found")

    logger.info("Import finished")

    return True

def do_cleanup():
    source_dir = os.path.join(settings.BASE_DIR, 'temp')
    list_of_files = glob.glob(os.path.join(source_dir, '*.csv'))
    for this_file in list_of_files:
        logger.info("Removing {}".format(this_file))
        os.remove(this_file)

    source_dir = os.path.join(settings.BASE_DIR, 'temp', 'alior')
    list_of_files = glob.glob(os.path.join(source_dir, '*.csv'))
    list_of_files += glob.glob(os.path.join(source_dir, '*.CSV'))
    for this_file in list_of_files:
        logger.info("Removing {}".format(this_file))
        os.remove(this_file)

    source_dir = settings.BASE_DIR
    destination_dir = os.path.join(settings.BASE_DIR, 'BACKUPS')
    list_of_files = glob.glob(os.path.join(source_dir, 'db.sqlite3'))
    for this_file in list_of_files:
        date_to_save = datetime.datetime.now().strftime("-%Y%m%d-%H%M%S")
        dest_file = this_file.replace('db.sqlite3', 'BACKUPS/db' + date_to_save + '.sqlite3')
        logger.info("Copying {} to {}".format(this_file, dest_file))
        shutil.copyfile(this_file, dest_file)
