from payme import app, stripe_keys
from flask import render_template, request
import stripe

stripe.api_key = stripe_keys['secret_key']

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents (integer)
    amount = request.form['sum2']
    currency = 'gbp'

    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency=currency,
        description='credit to cash'
    )

    amount = str(int(amount) / 100.0) + ' ' + currency.upper() 
    return render_template('charge.html', amount=amount_string)

if __name__ == '__main__':
    app.run()
