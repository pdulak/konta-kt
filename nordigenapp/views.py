from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from uuid import uuid4
from nordigen import NordigenClient
from loguru import logger
import environ
import os


def nordigen_calls():
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
    client = NordigenClient(
        secret_id=env('NORDIGEN_ID'),
        secret_key=env('NORDIGEN_SECRET')
    )

    #
    # https://github.com/nordigen/nordigen-python
    #

    # Create new access and refresh token
    # Parameters can be loaded from .env or passed as a string
    # Note: access_token is automatically injected to other requests after you successfully obtain it
    token_data = client.generate_token()

    # Use existing token
    # client.token = "YOUR_TOKEN"

    # Exchange refresh token for new access token
    # new_token = client.exchange_token(token_data["refresh"])

    # Get institution id by bank name and country
    # institution_id = client.institution.get_institution_id_by_name(
    #     country="LV",
    #     institution="Revolut"
    # )

    # Get all institution by providing country code in ISO 3166 format
    institutions = client.institution.get_institutions("PL")
    logger.info(institutions)

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


def get_list_of_banks():
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
    client = NordigenClient(
        secret_id=env('NORDIGEN_ID'),
        secret_key=env('NORDIGEN_SECRET')
    )
    token_data = client.generate_token()
    return client.institution.get_institutions("PL")

def initialize_bank_connection(institution_id):
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
    #Initialize bank session
    client = NordigenClient(
        secret_id=env('NORDIGEN_ID'),
        secret_key=env('NORDIGEN_SECRET')
    )
    token_data = client.generate_token()
    init = client.initialize_session(
        # institution id
        institution_id=institution_id,
        # redirect url after successful authentication
        redirect_uri="https://kontakt.dulare.com/nordigen/log_response/",
        # additional layer of unique ID defined by you
        reference_id=str(uuid4())
    )
    logger.info(init)

def list_requisitions():
    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))
    #Initialize bank session
    client = NordigenClient(
        secret_id=env('NORDIGEN_ID'),
        secret_key=env('NORDIGEN_SECRET')
    )
    token_data = client.generate_token()
    logger.info(client.requisition.get_requisitions())

@login_required(login_url='/auth/login/')
def bank_list(request):
    context = {
        'institutions': get_list_of_banks()
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
    # ALIOR_ALBPPLPW
    # MBANK_RETAIL_BREXPLPW
    # initialize_bank_connection('ALIOR_ALBPPLPW')
    list_requisitions()
    return render(request, 'nordigen/index.html')


