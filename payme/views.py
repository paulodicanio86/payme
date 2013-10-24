import os, stripe
from flask import (render_template, request, send_from_directory, redirect,
                   url_for)
from payme import app, stripe_keys, company
from string_functions import *


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
# /charge
#######################################
@app.route('/charge', methods=['POST'])
def charge():
    # get the values from the post
    variables = ['name', 'account_number', 'sort_code', 'reference', 'email', 'amount']
    values = {}
    for entry in variables:
        values[entry] = request.form[entry]
    valids = {}

    # convert fields
    values['name'] = convert_special_characters(values['name'])
    values['sort_code'] = convert_sort_code(values['sort_code'])
    values['reference'] = convert_special_characters(values['reference'])
    values['amount'] = convert_price(values['amount'])

    # validate entries
    valids['name'] = valid_name(values['name']) 
    valids['account_number'] = valid_account_number(values['account_number'])
    valids['sort_code'] = valid_sort_code(values['sort_code'])
    valids['reference'] = valid_reference(values['reference'])
    valids['email'] = valid_email(values['email'])
    valids['amount'] = valid_price(values['amount'])

    # reload if non validated entries exist
    if False in valids.values():
        dic_reload = {}
        for entry in variables:
            dic_reload[entry] = {'valid': valids[entry],
                                 'value': values[entry]}
        return default_pay(name_dic=dic_reload['name'],
                           account_number_dic=dic_reload['account_number'],
                           sort_code_dic=dic_reload['sort_code'],
                           reference_dic=dic_reload['reference'],
                           email_dic=dic_reload['email'],
                           amount_dic=dic_reload['amount'])
    else:
        return redirect(url_for('success', amount=values['amount']))

 
    # Make the customer
    customer = stripe.Customer.create(
        email=email,
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
            description=name + ' ' + reference
            )
    except stripe.CardError, e:
        # The card has been declined.
        return redirect(url_for('declined'))

    # add the payment to the database
    namecc = customer.cards.data[0].name    



    return redirect(url_for('success', amount=values['amount']))


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
