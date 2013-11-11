import os
from flask import Flask


company = 'PayMe'
domain = 'www.payme.com'
company_email = 'paul.schaack2+payment@gmail.com'
variable_names = ['name_receiver', 'account_number', 'sort_code', 'reference', 'amount', 'email_receiver', 'email_sender']
threshold = 100.00 # in [GBP]
card_usage_fee = 0.00 # in [GBP]
rate = 3.00 # in [%], to be charged when amount is over threshold. corresponds to 3.0928% in inverted mode.
fixed_fee = 3.00 # in [GBP], to be charged when amount is under threshold


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


