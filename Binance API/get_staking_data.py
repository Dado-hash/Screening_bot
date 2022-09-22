import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode
import api_keys
import api_keys_arcadia
import pandas as pd

BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': api_keys_arcadia.API_KEY
}

class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)

PATH = '/sapi/v1/staking/position'
timestamp = int(time.time() * 1000)
params = {
    'product': 'STAKING',
    'timestamp': timestamp,
    'recvWindow': 60000
}
query_string = urlencode(params)
params['signature'] = hmac.new(api_keys_arcadia.SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
url = urljoin(BASE_URL, PATH)
r = requests.get(url, headers=headers, params=params)
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
else:
    raise BinanceException(status_code=r.status_code, data=r.json())
df = pd.DataFrame(data)
df['purchaseTime'] = pd.to_datetime(df['purchaseTime']/1000, unit = 's')
df['interestEndDate'] = pd.to_datetime(df['interestEndDate']/1000, unit = 's')
df['deliverDate'] = pd.to_datetime(df['deliverDate']/1000, unit = 's')
numeric_columns = ['amount', 'rewardAmt', 'nextInterestPay', 'redeemAmountEarly', 'apy']
for c in numeric_columns:
    df[c] = df[c].str.replace(r'.', ',')
df.set_index('asset', inplace = True) 
#print(df)
#df.to_csv('esempio')
df.to_excel('staking.xlsx')

'''PATH_SUB = '/sapi/v3/sub-account/assets'
timestamp = int(time.time() * 1000)
params = {
    'email': '[EMAIL DEL SUBACCOUNT]',
    'timestamp': timestamp
}
query_string = urlencode(params)
params['signature'] = hmac.new(api_keys.SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
url = urljoin(BASE_URL, PATH_SUB)
r = requests.get(url, headers=headers, params=params)
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
else:
    raise BinanceException(status_code=r.status_code, data=r.json())'''



'''PATH_SNAPSHOT = '/sapi/v1/accountSnapshot'
timestamp = int(time.time() * 1000)
params = {
    'type': 'SPOT',
    'timestamp': timestamp,
    'recvWindow': 60000
}
query_string = urlencode(params)
params['signature'] = hmac.new(api_keys_arcadia.SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
url = urljoin(BASE_URL, PATH_SNAPSHOT)
r = requests.get(url, headers=headers, params=params)
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
else:
    raise BinanceException(status_code=r.status_code, data=r.json())'''


'''PATH_FLEXIBLE = '/sapi/v1/lending/daily/token/position'
timestamp = int(time.time() * 1000)
params = {
    'timestamp': timestamp,
    'recvWindow': 60000
}
query_string = urlencode(params)
params['signature'] = hmac.new(api_keys_arcadia.SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
url = urljoin(BASE_URL, PATH_FLEXIBLE)
r = requests.get(url, headers=headers, params=params)
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
else:
    raise BinanceException(status_code=r.status_code, data=r.json())'''