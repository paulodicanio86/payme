import os, stripe
from flask import (render_template, request, send_from_directory, redirect,
                   url_for)
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
        return redirect(url_for('declined'))

    amount_string = str(int(amount) / 100.0)
    return redirect(url_for('success', amount=amount_string))


#######################################
# /success/<amount>
#######################################
@app.route('/success/<amount>')
def success(amount, company=company):
    return render_template('charge.html',
                           amount=amount,
                           company=company)

#######################################
# /declined
#######################################
@app.route('/declined')
def declined():
    return render_template('declined.html',
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
