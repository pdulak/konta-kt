import datetime
import urllib3
import json


def get_nbp_rates():

    http = urllib3.PoolManager()
    r = http.request('GET', 'http://api.nbp.pl/api/exchangerates/tables/A/2019-07-04/?format=json')

    print(vars(r))

    # r.status = 200

    response = json.loads(r.data.decode('utf-8'))

    print(vars(response))

    return True
