import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from uuid import uuid4
from nordigen import NordigenClient
from loguru import logger
from datetime import datetime
from dateutil.relativedelta import relativedelta
import environ
import time
import os
import json
from json2html import *

from .models import NordigenTokens
from accounts.models import Account

is_nordigen_initialized = False
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
nordigen_client = NordigenClient(
    secret_id=env('NORDIGEN_ID'),
    secret_key=env('NORDIGEN_SECRET')
)


@login_required(login_url='/auth/login/')
def bank_list(request):
    context = {
        'institutions': get_list_of_banks(),
        'requisitions': list_requisitions(),
        'kontakt_accounts': get_accounts_with_assignments(),
    }
    return render(request, 'nordigen/bank_list.html', context)


@login_required(login_url='/auth/login/')
def force_token_refresh(request):
    nordigen_get_fresh_token()
    return render(request, 'nordigen/token_refreshed.html')


@login_required(login_url='/auth/login/')
def index(request):
    return render(request, 'nordigen/index.html')


@login_required(login_url='/auth/login/')
def log_response(request):
    logger.info(request.POST)
    return render(request, 'nordigen/index.html')


@login_required(login_url='/auth/login/')
def test(request):
    return render(request, 'nordigen/index.html')


@login_required(login_url='/auth/login/')
def connect_bank(request, institution_id):
    initialize_bank_connection(institution_id)
    return redirect('/nordigen/bank_list')


@login_required(login_url='/auth/login/')
def account_details(request, account_id):
    context = {
        'account_id': account_id,
        'details': get_account_details(account_id),
        'kontakt_accounts': get_accounts_with_assignments(),
    }
    return render(request, 'nordigen/account.html', context)


@login_required(login_url='/auth/login/')
def assign_account(request, kontakt_account_id, nordigen_account_id, iban):
    Account.objects.filter(id=kontakt_account_id).update(iban=iban, nordigen_id=nordigen_account_id)
    return render(request, 'nordigen/account_assignment_result.html')


@login_required(login_url='/auth/login/')
def account_transactions(request, account_id):
    context = {
        'account_id': account_id,
        'account_name' : '',
        'account_number' : '',
        'transactions': read_account_transactions_from_file_or_API(account_id)
    }
    for this_account in Account.objects.filter(nordigen_id=account_id):
        context['account_name'] = this_account.name
        context['account_number'] = this_account.number

    df = convert_transactions_to_dataframe(account_id, context['account_number'],
                                           context['transactions']['transactions']['booked'])

    return HttpResponse(df.to_html() + json2html.convert(context))


@login_required(login_url='/auth/login/')
def account_transactions_json(request, account_id):
    context = read_account_transactions_from_file_or_API(account_id)

    return JsonResponse(context['transactions']['booked'], safe=False)

def read_account_transactions_from_file_or_API(account_id):
    source_dir = os.path.join(settings.BASE_DIR, 'temp')
    file_name = datetime.today().strftime('%Y-%m-%d---') + account_id + '.json'
    file_path = os.path.join(source_dir, file_name)

    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        transactions = get_account_transactions(account_id, 30)

        with open(file_path, "w") as f:
            json.dump(transactions, f)

        return transactions


def convert_transactions_to_dataframe(account_id, account_number, transactions):
    data = []

    for boo in transactions:
        boo['transactionAmount']['amount'] = float(boo['transactionAmount']['amount'])

        if boo['transactionAmount']['amount'] < 0:
            party_name = ''
            if 'creditorName' in boo.keys():
                party_name = boo['creditorName']
            elif 'remittanceInformationUnstructured' in boo.keys():
                party_name = boo['remittanceInformationUnstructured']
            elif 'remittanceInformationUnstructuredArray' in boo.keys():
                party_name = " ".join(boo['remittanceInformationUnstructuredArray'])

            party_iban = ''
            if 'creditorAccount' in boo.keys():
                party_iban = boo['creditorAccount']['iban']

        else:
            party_name = ''
            if 'debtorName' in boo.keys():
                party_name = boo['debtorName']
            elif 'remittanceInformationUnstructured' in boo.keys():
                party_name = boo['remittanceInformationUnstructured']
            elif 'remittanceInformationUnstructuredArray' in boo.keys():
                party_name = " ".join(boo['remittanceInformationUnstructuredArray'])

            party_iban = ''
            if 'debtorAccount' in boo.keys():
                party_iban = boo['debtorAccount']['iban']

        transaction_type = 'OUT' if boo['transactionAmount']['amount'] <= 0 else 'IN'
        if 'proprietaryBankTransactionCode' in boo.keys():
            transaction_type = boo['proprietaryBankTransactionCode']

        balance = 0
        if 'balanceAfterTransaction' in boo.keys():
            if 'balanceAmount' in boo['balanceAfterTransaction'].keys():
                if 'amount' in boo['balanceAfterTransaction']['balanceAmount'].keys():
                    balance = boo['balanceAfterTransaction']['balanceAmount']['amount']

        description = ''
        if 'remittanceInformationUnstructured' in boo.keys():
            description = boo['remittanceInformationUnstructured']
        elif 'remittanceInformationUnstructuredArray' in boo.keys():
            description = " ".join(boo['remittanceInformationUnstructuredArray'])

        this_transaction = [boo['valueDate'],
                            boo['valueDate'],
                            description,
                            boo['transactionAmount']['amount'],
                            balance,
                            account_id,
                            transaction_type,
                            party_name,
                            party_iban,
                            account_number.replace(' ', ''),
                            boo['valueDate'],
                            boo['transactionAmount']['amount'],
                            balance,
                            boo['internalTransactionId'],
                            1
                            ]

        data.append(this_transaction)

    field_names = ['Date', 'Added', 'Description', 'Amount', 'Balance', 'Source', 'Type', 'Party Name', 'Party IBAN',
                   'Account Number', 'Date Modified', 'Amount Modified', 'Balance Modified', 'Transaction ID', 'isNordigen']

    return pd.DataFrame(data, columns=field_names)


def get_accounts_with_assignments():
    return Account.objects.select_related('bank') \
        .values('name', 'number', 'bank__name', 'id', 'nordigen_id') \
        .order_by('bank__name', 'name')

def nordigen_get_fresh_token():
    global is_nordigen_initialized, nordigen_client
    token_data = nordigen_client.generate_token()
    NordigenTokens.objects.create(
        access=token_data["access"],
        refresh=token_data["refresh"],
        access_expiration=datetime.fromtimestamp(time.time() + token_data["access_expires"]),
        refresh_expiration=datetime.fromtimestamp(time.time() + token_data["refresh_expires"])
    )
    is_nordigen_initialized = True


def nordigen_exchange_token(refresh_token, refresh_expiration):
    global is_nordigen_initialized, nordigen_client
    token_data = nordigen_client.exchange_token(refresh_token)
    logger.info(token_data)
    NordigenTokens.objects.create(
        access=token_data["access"],
        refresh=refresh_token,
        access_expiration=datetime.fromtimestamp(time.time() + token_data["access_expires"]),
        refresh_expiration=refresh_expiration
    )
    is_nordigen_initialized = True


def noridgen_initialize():
    global is_nordigen_initialized, nordigen_client

    if (is_nordigen_initialized):
        logger.info('Nordigen initialized, nothing to do')
        return nordigen_client
    else:
        logger.info('Generating Nordigen token')
        last_token = NordigenTokens.objects.order_by('-id')[:1]
        if (last_token.exists()):
            for token in last_token:
                if token.access_expiration.timestamp() > time.time():
                    # token is fresh
                    logger.info("Stored Nordigen token is fresh")
                    nordigen_client.token = token.access
                    is_nordigen_initialized = True
                    return nordigen_client
                elif token.refresh_expiration.timestamp() > time.time():
                    # refresh token
                    logger.info("Stored Nordigen token is old, but can be refreshed")
                    nordigen_exchange_token(token.refresh, token.refresh_expiration)
                    return nordigen_client
                else:
                    # everything too old, create a new one
                    nordigen_get_fresh_token()
        else:
            # not exists in the DB
            nordigen_get_fresh_token()

    logger.info('Nordigen initialized')
    return nordigen_client


def get_list_of_banks():
    client = noridgen_initialize()
    return client.institution.get_institutions("PL")


def initialize_bank_connection(institution_id):
    client = noridgen_initialize()
    init = client.initialize_session(
        # institution id
        institution_id=institution_id,
        # redirect url after successful authentication
        redirect_uri="https://kontakt.dulare.com/nordigen/log_response/",
        # additional layer of unique ID defined by you
        reference_id=str(uuid4())
    )


def list_requisitions():
    client = noridgen_initialize()
    return client.requisition.get_requisitions()


def get_account_details(account_id):
    client = noridgen_initialize()
    account = client.account_api(id=account_id)
    return account.get_details()


def get_account_transactions(account_id, days=20):
    client = noridgen_initialize()
    account = client.account_api(id=account_id)
    start_date = (datetime.now() - relativedelta(days=days)).strftime("%Y-%m-%d")
    return account.get_transactions(date_from=start_date)