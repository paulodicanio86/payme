import os
from flask import Flask


company = 'PayMe'
domain = 'www.payme.com'
variable_names = ['name', 'account_number', 'sort_code', 'reference', 'email', 'amount', 'email_account']
threshold = 100.00 # in [GBP]
card_usage_fee = 0.00 # in [GBP]
rate = 3.00 # in [%] over threshold
fixed_fee = 3.00 # in [GBP] under threshold

email_account = {
    'user': 'paul.schaack2@gmail.com',
    'password': os.environ['EMAIL_PWD'],
    'server': 'smtp.gmail.com',
    'port': 587,
    'from': 'paul.schaack2@gmail.com'
}

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}


app = Flask(__name__)

import payme.views


