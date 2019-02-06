import datetime

from .models import ImportHeader
from accounts.models import Account
from transactions.models import Transaction, TransactionImportTemp


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

                # check for transaction duplicate
                is_duplicate = False

                chk_transaction = Transaction.objects.filter(date=row['Date Modified'][:10],
                                                             account=accounts_numbers[row['Account Number']],
                                                             amount_account_currency=row['Amount Modified'],
                                                             balance_account_currency=row['Balance Modified'],
                                                             imported_description__contains=row['Description']
                                                             ).count()

                if chk_transaction > 0:
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
                print("Account number ", row['Account Number'], " not found")

    else:
        print('Accounts with numbers not found')

    print('--------------------------------------------------------')
    print(datetime.datetime.now(), ' import finished')

    return True
