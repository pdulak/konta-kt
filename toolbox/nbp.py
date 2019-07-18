import datetime
import urllib3
import json
from datetime import datetime, timedelta
from loguru import logger

# get table from the particular date
# if there is an error, get from the earlier date, limit to 14 days back
# if no error, find particular currency

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
