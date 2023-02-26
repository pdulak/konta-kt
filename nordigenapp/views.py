from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from uuid import uuid4
from nordigen import NordigenClient
from loguru import logger
import environ
import os


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
        pass
    else:
        token_data = nordigen_client.generate_token()
        logger.info(token_data)
        logger.info(nordigen_client.token)
        is_nordigen_initialized = True
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
    logger.info(init)

def list_requisitions():
    client = noridgen_initialize()
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


