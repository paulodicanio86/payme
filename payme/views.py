import os
from flask import render_template, request, send_from_directory
import stripe

from payme import app, stripe_keys, company


stripe.api_key = stripe_keys['secret_key']


#######################################
# /
#######################################
@app.route('/')
def index():
    return render_template('index.html',
                           key=stripe_keys['publishable_key'],
                           company=company)


#######################################
# /charge
#######################################
@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents (integer)
    amount = request.form['sum2']
    currency = 'gbp'

    # Make the customer
    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency=currency,
            description='credit to cash'
            )
    except stripe.CardError, e:
        # The card has been declined.
        pass
        return render_template('declined.html',
                               company=company)

    amount = str(int(amount) / 100.0) + ' ' + currency.upper() 
    return render_template('charge.html',
                           amount=amount,
                           company=company)


#######################################
# Error 404
#######################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', company=company), 404


#######################################
# Favicon (also done in layout.html)
#######################################
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')



if __name__ == '__main__':
    app.run()
