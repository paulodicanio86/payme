import os
from flask import Flask
from mongokit import Connection
from payme.db_entry import Payment

company = 'PayMe'
domain = 'www.payme.com'
company_email = 'paul.schaack2+payment@gmail.com'
company_info_email = 'paul.schaack2+payme_info@gmail.com'


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


# database configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017


app = Flask(__name__)
app.config.from_object(__name__)


# set the secret key. keep this really secret:
app.secret_key = '\xa8\xe2\x0f\xcd\xb4\xfby\xb0\x16\xaa/i\xfam8\x8e\xd7\xd5\xb5\x1e\x10\x93\xee+'


# connect to the database
connection = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])
connection.register([Payment])


import payme.views
