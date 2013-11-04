from __future__ import division, print_function, absolute_import

import os
import stripe
from flask import (render_template, request, send_from_directory, redirect,
                   url_for)

from payme import app, stripe_keys, company, variable_names
from payme.validation_functions import *


stripe.api_key = stripe_keys['secret_key']


#######################################
# function to make default pay page
#######################################
default_dic = {'valid': True,
               'value': '',
               'read_only': False,
               'hidden': False}

def default_pay(name_dic=default_dic,
                account_number_dic=default_dic,
                sort_code_dic=default_dic,
                reference_dic=default_dic,
                email_dic=default_dic,
                amount_dic=default_dic,
                email_account_dic=default_dic,
                add_fee=True,):
    
    return render_template('pay.html',
                           key=stripe_keys['publishable_key'],          
                           name=name_dic,
                           account_number=account_number_dic,
                           sort_code=sort_code_dic,
                           reference=reference_dic,
                           email=email_dic,
                           amount=amount_dic,
                           email_account=email_account_dic,
                           add_fee=add_fee,
                           company=company)


#######################################
# /, /pay, /custom/
#######################################
@app.route('/')
@app.route('/pay')
@app.route('/custom/')
def index():
    return default_pay()


#######################################
# /verify
#######################################
@app.route('/verify', methods=['GET'])
def verify_get():
    return redirect(url_for('index'))

@app.route('/verify', methods=['POST'])
def verify_post():
    # get the values from the post
    values = {}
    valids = {}
    read_only = {}
    # fill, convert and validate entries
    for entry in variable_names:
        values[entry] = request.form[entry]
        values[entry] = convert_entries(entry, values[entry])
        valids[entry] = validate_entries(entry, values[entry])
        read_only[entry] = get_boolean(request.form['read_only_' + entry])

    # reload if non-validated entries exist
    if False in valids.values():
        arg_dic = {'add_fee': request.form['add_fee']}
        for entry in variable_names:
            arg_dic[entry + '_dic'] = {'valid': valids[entry],
                                       'value': values[entry],
                                       'read_only': read_only[entry]}
        return default_pay(**arg_dic)
    else:
        return charge(payment=values, add_fee=get_boolean(request.form['add_fee']))


#######################################
# /charge
######################################
@app.route('/charge', methods=['GET'])
def charge_get():
    return redirect(url_for('index'))

def charge(payment, add_fee):
    payment['fee'] = get_fee(payment['amount'], add_fee)

    # determine whether charge is included or not
    if add_fee:
        payment['amount_orig'] = payment['amount']
        payment['pay_out'] = payment['amount']

        # update chargeable amount with fee:
        total = two_digit_string(float(payment['amount']) + float(payment['fee']))
        payment['amount'] = total 
        payment['fee_stripe'] = get_fee_stripe(total)
    else:
        payment['amount_orig'] = payment['amount']
        payment['pay_out'] = two_digit_string(float(payment['amount'])
                                              - float(payment['fee']))

        payment['fee_stripe'] = get_fee_stripe(payment['amount'])

    # For stripe amount label we require the amount in whole pence
    payment['amount_pence'] = price_in_pence(payment['amount'])
   
    return render_template('charge.html',
                           key=stripe_keys['publishable_key'],
                           payment=payment,
                           add_fee=add_fee,
                           company=company)

@app.route('/charge', methods=['POST'])
def charge_post():
    # get the values from the post
    values = {}
    for entry in variable_names + ['fee', 'fee_stripe', 'pay_out']:
        values[entry] = request.form[entry]
        
    # make the customer
    customer = stripe.Customer.create(
        email=values['email'],
        card=request.form['stripeToken']
        )

    # create the charge on stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=price_in_pence(values['amount']), # required by stripe in pence
            currency='gbp',
            description=(values['pay_out'] 
                         + ' ' + values['name'] 
                         + ' ' + values['reference'])
            )
    except stripe.CardError, e: # The card has been declined.
        return redirect(url_for('declined'))


    # add the payment to the database
    name_payer = customer.cards.data[0].name
    email_payer = values['email']
    name_receiver = values['name']
    email_receiver = values['email_account']
    account_number = values['account_number']
    sort_code = values['sort_code']
    reference = values['reference']

    pay_out = float(values['pay_out']) # this needs to be paid out to receiver
    charged = float(values['amount']) # this is what was charged from cc card
    fee = float(values['fee']) # this is my fee
    fee_stripe = float(values['fee_stripe']) # this is stripe's fee

    paid_in = charged - fee_stripe # this is what will reach my account
    profit = paid_in - pay_out # this is what I can keep
    profit2 = fee - fee_stripe # this should be the same - (better, as usually exactly 2 digits)
    check_sum = profit - profit2 # and this should be 0.0

    print (name_payer, 
           email_payer,
           name_receiver, 
           email_receiver,
           fee_stripe,
           fee,
           pay_out,
           charged,
           paid_in,
           profit,
           profit2,
        check_sum)


    # Function to send emails for:
    # if provided, send an email to 'email' (payer), notifying him that he was successfully charged
    #... try:
    # if provided, send an email to 'email_receiver', notifying him that he will get paid a certain sum 
    #... try:
    # send an email to me with whome to pay how much money (to receiver, then what my share is)
    #... try:
    
    return redirect(url_for('success', amount=values['amount']))





#######################################
# /custom/<account_number>/<sort_code>/<name>/
#######################################
@app.route('/custom/<account_number>/<sort_code>/<name>/')
def custom(account_number, sort_code, name, 
           amount = '', company=company):

    local_variable_names = ['account_number', 'sort_code', 'name', 'amount']
    local_variable_values = [locals()[f] for f in local_variable_names]

    values = {}
    valids = {}
    read_only = {}
    # fill, convert and validate entries
    for i, entry in enumerate(local_variable_names):
        values[entry] = local_variable_values[i]
        values[entry] = convert_entries(entry, values[entry])
        valids[entry] = validate_entries(entry, values[entry])
        read_only[entry] = get_boolean(valids[entry])
        
    arg_dic = {}
    for entry in local_variable_names:
        arg_dic[entry + '_dic'] = {'valid': valids[entry],
                                   'value': values[entry],
                                   'read_only': read_only[entry]}

    #special modifications
    arg_dic['amount_dic']['valid'] = True
    arg_dic['add_fee'] = False

    return default_pay(**arg_dic)


#######################################
# /custom/<account_number>/<sort_code>/<name>/<amount>/
#######################################
@app.route('/custom/<account_number>/<sort_code>/<name>/<amount>/')
def custom_amount(account_number, sort_code, name, amount, 
                  reference='', email_account='', email='',
                  checked=True, company=company):

    local_variable_values = [locals()[f] for f in variable_names]
   
    add_fee = False

    values = {}
    valids = {}
    read_only = {}
    # fill, convert and validate entries
    for i, entry in enumerate(variable_names):
        values[entry] = local_variable_values[i]
        values[entry] = convert_entries(entry, values[entry])
        valids[entry] = validate_entries(entry, values[entry])
        read_only[entry] = get_boolean(valids[entry])

    # reload if non-validated entries exist
    if False in (valids.values() + [checked]):
        arg_dic = {'add_fee': add_fee}
        for entry in variable_names:
            arg_dic[entry + '_dic'] = {'valid': valids[entry],
                                       'value': values[entry],
                                       'read_only': read_only[entry]}

        #special modifications
        if values['reference']=='':
            arg_dic['reference_dic']['read_only'] = False
        if values['email']=='':
            arg_dic['email_dic']['read_only'] = False
        if values['amount']=='blank':
            arg_dic['amount_dic']['read_only'] = False
            arg_dic['amount_dic']['valid'] = True
            arg_dic['amount_dic']['value'] = ''
        return default_pay(**arg_dic)
    else:
        return charge(payment=values, add_fee=add_fee)
    

#######################################
# /custom/<account_number>/<sort_code>/<name>/<amount>/<reference>/
#######################################
@app.route('/custom/<account_number>/<sort_code>/<name>/<amount>/<reference>/')
def custom_reference(account_number, sort_code, name, amount,
                     reference):
    return custom_amount(account_number, sort_code, name, amount,
                         reference)


#######################################
# /custom/<account_number>/<sort_code>/<name>/<amount>/<reference>/<email_account>/
#######################################
@app.route('/custom/<account_number>/<sort_code>/<name>/<amount>/<reference>/<email_account>/')
def custom_email(account_number, sort_code, name, amount,
                 reference, email_account):
    return custom_amount(account_number, sort_code, name, amount,
                         reference, email_account)


#######################################
# /success/<float:amount>
#######################################
@app.route('/success/<float:amount>')
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
