import os
from flask import Flask

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

company = 'PayMe'
variable_names = ['name', 'account_number', 'sort_code', 'reference', 'email', 'amount']


app = Flask(__name__)

import payme.views


