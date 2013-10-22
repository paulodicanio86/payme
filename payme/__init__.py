import os
from flask import Flask

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

app = Flask(__name__)

import payme.views


