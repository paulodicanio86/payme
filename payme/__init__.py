import os
from flask import Flask


company = 'PayMe'
variable_names = ['name', 'account_number', 'sort_code', 'reference', 'email', 'amount']
rate = 3.00 # in %
threshold = 100.00 # in GBP
card_usage_fee = 0.00 # in GBP
fixed_fee = 3.00 # in GBP

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}


app = Flask(__name__)

import payme.views


