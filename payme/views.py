import os, stripe
from flask import (render_template, request, send_from_directory, redirect,
                   url_for)
from payme import app, stripe_keys, company, variable_names
from validation_functions import *


stripe.api_key = stripe_keys['secret_key']


#######################################
# function to make default pay page
#######################################
default_dic = {'valid': True,
               'value': '',
               'disabled': False,
               'hidden': False}

def default_pay(name_dic=default_dic,
                account_number_dic=default_dic,
                sort_code_dic=default_dic,
                reference_dic=default_dic,
                email_dic=default_dic,
                amount_dic=default_dic):
    return render_template('pay.html',
                           key=stripe_keys['publishable_key'],
                           name=name_dic,
                           account_number=account_number_dic,
                           sort_code=sort_code_dic,
                           reference=reference_dic,
                           email=email_dic,
                           amount=amount_dic,
                           company=company)


#######################################
# /, /pay
#######################################
@app.route('/')
@app.route('/pay')
def index():
    return default_pay()


#######################################
# /verify
#######################################
@app.route('/verify', methods=['GET'])
def verify_get():
    redirect(url_for('pay')) #or 'index'?

@app.route('/verify', methods=['POST'])
def verify_post():
    # get the values from the post
    values = {}
    valids = {}
    # fill, convert and validate entries
    for entry in variable_names:
        values[entry] = request.form[entry]
    values = convert_entries(values)
    valids = validate_entries(valids, values)

    # reload if non-validated entries exist
    if False in valids.values():
        dic_reload = {}
        for entry in variable_names:
            dic_reload[entry] = {'valid': valids[entry],
                                 'value': values[entry]}
        return default_pay(name_dic=dic_reload['name'],
                           account_number_dic=dic_reload['account_number'],
                           sort_code_dic=dic_reload['sort_code'],
                           reference_dic=dic_reload['reference'],
                           email_dic=dic_reload['email'],
                           amount_dic=dic_reload['amount'])
    else:
        return charge(payment=values)


#######################################
# /charge
#######################################
def charge(payment):


    #HERE, two things:
    # 1. add fee (2.4% + 0.20p for stripe. make 3gbp <100.00, then 3%?)
    # check if minimum payment 0.50p

    
    # For stripe amount label we require the amount in whole pence
    payment['amount2'] = price_in_pence(payment['amount'])

    return render_template('charge.html',
                           key=stripe_keys['publishable_key'],
                           payment=payment,
                           company=company)

@app.route('/charge', methods=['GET'])
def charge_get():
    redirect(url_for('pay')) #or 'index'?
    
@app.route('/charge', methods=['POST'])
def charge_post():
    # get the values from the post
    values = {}
    valids = {}
    # fill, convert and validate entries
    for entry in variable_names:
        values[entry] = request.form[entry]
    values = convert_entries(values)
    valids = validate_entries(valids, values)

    # reload if non-validated entries exist
    if False in valids.values():
        dic_reload = {}
        for entry in variable_names:
            dic_reload[entry] = {'valid': valids[entry],
                                 'value': values[entry]}
        return default_pay(name_dic=dic_reload['name'],
                           account_number_dic=dic_reload['account_number'],
                           sort_code_dic=dic_reload['sort_code'],
                           reference_dic=dic_reload['reference'],
                           email_dic=dic_reload['email'],
                           amount_dic=dic_reload['amount'])

    # Make the customer
    customer = stripe.Customer.create(
        email=values['email'],
        card=request.form['stripeToken']
        )

    # Create the charge on Stripe's servers - this will charge the user's card
    currency = 'gbp'
    amount = price_in_pence(values['amount']) # convert to pence (required by stripe)
    try:
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency=currency,
            description=values['name'] + ' ' + values['reference']
            )
    except stripe.CardError, e:
        # The card has been declined.
        return redirect(url_for('declined'))

    # add the payment to the database
    namecc = customer.cards.data[0].name    
    # send an email to customer if provided
    #... try:
    # send an email to me with P&L, \n
    #... try:
    
    return redirect(url_for('success', amount=values['amount']))


#######################################
# /success/<amount>
#######################################
@app.route('/success/<amount>')
def success(amount, company=company):
    return render_template('success.html',
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
