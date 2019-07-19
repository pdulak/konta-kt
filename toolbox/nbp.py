import datetime
import urllib3
import json
from datetime import datetime, timedelta
from loguru import logger
from transactions.models import Transaction
from decimal import Decimal

# find all transactions in currency other than PLN
# check if the rate is set
# set the rate and recalculate if needed


def get_nbp_rate_table_a(date_to_get=datetime.now(), currency_code_to_get='EUR'):
    """Gets the A currency table from NBP for the particular date and currency code

        date_to_get - the date to get the table from
        currency_code_to_get - the currency code to get from the table

        Returns False if no table found for the particular date
        or no currency found for the particular code
    """
    logger.info("called with {}, {}".format(date_to_get, currency_code_to_get))
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://api.nbp.pl/api/exchangerates/tables/A/{}/?format=json'.format(date_to_get.strftime('%Y-%m-%d')))
    if r.status == 200:
        for r in json.loads(r.data.decode('utf-8'))[0]['rates']:
            if r['code'] == currency_code_to_get:
                logger.info("found rate of {} for {}: {}".format(currency_code_to_get, date_to_get, r['mid']))
                return r['mid']

    return False


def get_nbp_rate_table_a_with_backtrack(date_to_get=datetime.now(), currency_code_to_get='EUR'):
    """Gets the A currency table from NBP for the particular date and currency code.
        If no table found for the particular date, the function is changing the date to the previous day,
        this operation is repeated no more than 14 times (14 days back)

        date_to_get - the date to get the table from
        currency_code_to_get - the currency code to get from the table

        Returns False if no table found for the particular date and previous days
        or no currency found for the particular code
    """
    for d in range(0, 15):
        result = get_nbp_rate_table_a(date_to_get - timedelta(d), currency_code_to_get)
        if result:
            return result

    return False


def check_non_pln_transactions():
    """Check the transactions in currencies other than PLN and adjusts the rate"""

    # get the transactions list to update (non-PLN, currency multiplier not set)
    t = Transaction.objects
    t = t.select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .exclude(account__currency__name='PLN') \
        .filter(currency_multiplier=1) \
        .values('id', 'account__currency__name') \
        .order_by('date')

    logger.info("Found {} NON-PLN transactions to update".format(t.count()))

    # update one by one
    for tt in t:
        adjust_non_pln_transaction_rate(tt['id'], tt['account__currency__name'])

    return t.count()


def check_pln_transactions():
    """Check the transactions in PLN and adjusts the rate if wrong"""

    # get the transactions list to update (non-PLN, currency multiplier not set)
    t = Transaction.objects
    t = t.select_related('account') \
        .select_related('bank') \
        .select_related('currency') \
        .exclude(currency_multiplier=1) \
        .filter(account__currency__name='PLN') \
        .values('id') \
        .order_by('date')

    logger.info("Found {} PLN transactions to update".format(t.count()))

    # update one by one
    for tt in t:
        adjust_pln_transaction_rate(tt['id'])

    return t.count()


def adjust_non_pln_transaction_rate(transaction_id, currency_code):
    """Adjust non-PLN transaction to set proper rate and values"""

    this_transaction = Transaction.objects.get(pk=transaction_id)
    logger.info("Updating {}".format(this_transaction))
    rate_to_set = get_nbp_rate_table_a_with_backtrack(this_transaction.date, currency_code)
    if rate_to_set:
        logger.info("rate for this transaction: {}".format(rate_to_set))
        this_transaction.currency_multiplier = Decimal(rate_to_set)
        this_transaction.amount = this_transaction.amount_account_currency * Decimal(rate_to_set)
        logger.info("new transaction values: {}".format(this_transaction))
        this_transaction.save()


def adjust_pln_transaction_rate(transaction_id):
    """Adjust PLN transaction to set proper rate and values"""

    this_transaction = Transaction.objects.get(pk=transaction_id)
    logger.info("Updating {}".format(this_transaction))
    this_transaction.currency_multiplier = 1
    this_transaction.amount = this_transaction.amount_account_currency
    this_transaction.save()
