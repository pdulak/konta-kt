from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from uuid import uuid4
from nordigen import NordigenClient
from loguru import logger
import environ
import os

from accounts.models import Account

is_nordigen_initialized = False
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
nordigen_client = NordigenClient(
    secret_id=env('NORDIGEN_ID'),
    secret_key=env('NORDIGEN_SECRET')
)


def noridgen_initialize():
    global is_nordigen_initialized, nordigen_client
    if (is_nordigen_initialized):
        logger.info('Nordigen initialized, nothing to do')
    else:
        logger.info('Generating Nordigen token')
        token_data = nordigen_client.generate_token()
        # logger.info(token_data)
        # logger.info(nordigen_client.token)
        is_nordigen_initialized = True
        logger.info('Nordigen initialized')
    return nordigen_client


def nordigen_calls():
    #
    # https://github.com/nordigen/nordigen-python
    #

    # Exchange refresh token for new access token
    # new_token = client.exchange_token(token_data["refresh"])

    # Initialize bank session
    # init = client.initialize_session(
    #     # institution id
    #     institution_id=institution_id,
    #     # redirect url after successful authentication
    #     redirect_uri="https://nordigen.com",
    #     # additional layer of unique ID defined by you
    #     reference_id=str(uuid4())
    # )

    # Get requisition_id and link to initiate authorization process with a bank
    # link = init.link  # bank authorization link
    # requisition_id = init.requisition_id
    pass


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
    # {
    #     # Fetch account metadata
    #     'meta_data': account.get_metadata(),
    #     # Fetch details
    #     'details': account.get_details(),
    #     # Fetch balances
    #     'balances': account.get_balances(),
    #     # Fetch transactions
    #     'transactions': account.get_transactions(),
    # }


@login_required(login_url='/auth/login/')
def bank_list(request):
    context = {
        'institutions': get_list_of_banks(),
        'requisitions': list_requisitions(),
        'kontakt_accounts': get_accounts_with_assignments(),
    }
    return render(request, 'nordigen/bank_list.html', context)


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

def get_accounts_with_assignments():
    return Account.objects.select_related('bank') \
        .values('name', 'number', 'bank__name', 'id', 'nordigen_id') \
        .order_by('bank__name', 'name')
