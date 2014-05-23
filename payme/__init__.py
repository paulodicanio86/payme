import os
from flask import Flask
##from mongokit import Connection
##from payme.db_entry import Payment

def get_bool(value):
    '''
    converts a string into a boolean value
    '''
    if str(value)=='True':
        return True
    else:
        return False

######################
# Settings
######################

active = get_bool(os.environ['ONLINE']) # turn webpage on/off
print('-----------------',os.environ['ONLINE'], active)
company = 'NicerPay'
domain = 'www.nicerpay.com'
company_email = 'info@nicerpay.com'
company_info_email = 'info@nicerpay.com'


variable_names = ['name_receiver', 'account_number', 'sort_code', 'reference', 'amount', 'email_receiver']
currency = 'gbp' # required for stripe
currency_html = '<span class="glyphicon glyphicon-cutlery"></span>' # knife and fork symbol
currency_html = '<i class="fa fa-gbp"></i>' # Fancy pound symbol
currency_html = '&pound;' # HTML pound symbol


threshold = 100.00 # in [GBP], threshold for minimum charge (fixed_fee)
card_usage_fee = 0.00 # in [GBP]
rate = 3.00 # in [%], to be charged when amount is over threshold. corresponds to 3.0928% in inverted mode.
fixed_fee = 3.00 # in [GBP], to be charged when amount is under threshold


email_account = {
    'user': company_email,
    'password': os.environ['EMAIL_PWD'],
    'server': 'smtp.zoho.com',
    'port': 465,
    'from': company_email
}


stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}


app = Flask(__name__)
app.config.from_object(__name__)


# set the secret key. keep this really secret:
app.secret_key = '\xa8\xe2\x0f\xcd\xb4\xfby\xb0\x16\xaa/i\xfam8\x8e\xd7\xd5\xb5\x1e\x10\x93\xee+'


# database configuration
##MONGODB_HOST = 'localhost'
##MONGODB_PORT = 27017


# connect to the database
##db_connection = Connection(app.config['MONGODB_HOST'],
##                        app.config['MONGODB_PORT'])
##db_connection.register([Payment])


import payme.views
