import glob
import os
import datetime
import shutil
import base64
import hashlib
import json

import pandas as pd
import requests
from dotenv import load_dotenv
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

        duplicates = []
        imported = []

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

                if row['import_source'] == 'Nordigen':
                    chk_transaction_nordigen = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                                     account=accounts_numbers[row['Account Number']],
                                                                     amount_account_currency=row['Amount Modified'],
                                                                     import_source='Nordigen'
                                                                 ) \
                        .exclude(import_header=import_headers[row['Source']]) \
                        .count()

                    chk_transaction_csv = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                                 account=accounts_numbers[row['Account Number']],
                                                                 amount_account_currency=row['Amount Modified'],
                                                                 )\
                        .exclude(import_source='Nordigen')\
                        .exclude(import_header=import_headers[row['Source']])\
                        .count()
                else:
                    chk_transaction_nordigen = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                                          account=accounts_numbers[
                                                                              row['Account Number']],
                                                                          amount_account_currency=row[
                                                                              'Amount Modified'],
                                                                          import_source='Nordigen',
                                                                          ) \
                        .exclude(import_header=import_headers[row['Source']]) \
                        .count()

                    chk_transaction_csv = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                                     account=accounts_numbers[row['Account Number']],
                                                                     amount_account_currency=row['Amount Modified'],
                                                                     balance_account_currency=row['Balance Modified'],
                                                                     imported_description__contains=row['Description']
                                                                     )\
                        .exclude(import_source='Nordigen') \
                        .exclude(import_header=import_headers[row['Source']]) \
                        .count()

                chk_transaction = chk_transaction_nordigen + chk_transaction_csv

                if chk_transaction:
                    is_duplicate = True
                    duplicates.append(row)
                else:
                    # insert if not duplicate
                    imported.append(row)
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
                        party_IBAN=row['Party IBAN'],
                        transaction_id=row['Transaction ID'],
                        import_source=row['import_source']
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
                    is_duplicate=is_duplicate,
                    transaction_id=row['Transaction ID'],
                    import_source=row['import_source']
                )
            else:
                logger.warning("Account number {} not found".format(row['Account Number']))

    else:
        logger.warning("Accounts with numbers not found")

    logger.info("Import finished")

    df_duplicates = pd.concat(duplicates, axis=1).transpose() if len(duplicates) else pd.DataFrame()
    df_imported = pd.concat(imported, axis=1).transpose() if len(imported) else pd.DataFrame()

    return df_duplicates, df_imported

def do_cleanup():
    # Load environment variables from .env file
    load_dotenv()

    source_dir = os.path.join(settings.BASE_DIR, 'temp')
    list_of_files = glob.glob(os.path.join(source_dir, '*.csv'))
    list_of_files += glob.glob(os.path.join(source_dir, '*.json'))
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

        # Upload the backup file to Backblaze B2 using direct API calls
        try:
            # Get B2 credentials from environment variables
            key_id = os.environ.get('KEY_ID_PRIVATE')
            application_key = os.environ.get('APPLICATION_KEY_PRIVATE')
            bucket_id = os.environ.get('BUCKET_ID')

            if key_id and application_key and bucket_id:
                # Step 1: Authenticate and get authorization token
                auth_string = f"{key_id}:{application_key}"
                auth_encoded = base64.b64encode(auth_string.encode()).decode()

                auth_response = requests.get(
                    "https://api.backblazeb2.com/b2api/v2/b2_authorize_account",
                    headers={"Authorization": f"Basic {auth_encoded}"}
                )

                if auth_response.status_code != 200:
                    logger.error(f"B2 authentication failed: {auth_response.text}")
                    return

                auth_data = auth_response.json()
                auth_token = auth_data['authorizationToken']
                api_url = auth_data['apiUrl']
                download_url = auth_data['downloadUrl']

                # Step 2: Get upload URL
                get_upload_url_response = requests.get(
                    f"{api_url}/b2api/v2/b2_get_upload_url",
                    headers={
                        "Authorization": auth_token
                    },
                    params={"bucketId": bucket_id}
                )

                if get_upload_url_response.status_code != 200:
                    logger.error(f"Failed to get upload URL: {get_upload_url_response.text}")
                    return

                upload_data = get_upload_url_response.json()
                upload_url = upload_data['uploadUrl']
                upload_auth_token = upload_data['authorizationToken']

                # Step 3: Upload the file
                backup_filename = os.path.basename(dest_file)
                logger.info(f"Uploading {backup_filename} to B2 bucket {bucket_id}")

                with open(dest_file, 'rb') as file:
                    file_data = file.read()

                # Calculate SHA1 hash
                sha1_hash = hashlib.sha1(file_data).hexdigest()

                upload_response = requests.post(
                    upload_url,
                    headers={
                        "Authorization": upload_auth_token,
                        "X-Bz-File-Name": backup_filename,
                        "Content-Type": "application/octet-stream",
                        "X-Bz-Content-Sha1": sha1_hash
                    },
                    data=file_data
                )

                if upload_response.status_code == 200:
                    logger.info("Upload to B2 completed successfully")
                else:
                    logger.error(f"Upload failed: {upload_response.text}")
            else:
                logger.warning("B2 credentials not found in environment variables. Skipping upload.")
        except Exception as e:
            logger.error("Error uploading to B2: {}".format(str(e)))
