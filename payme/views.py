from payme import app, stripe_keys
from flask import render_template, request
import stripe

stripe.api_key = stripe_keys['secret_key']

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 5000

    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='gbp',
        description='credit to cash'
    )
    return render_template('charge.html', amount=amount)

if __name__ == '__main__':
    app.run()
