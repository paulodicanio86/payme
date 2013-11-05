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

def default_pay(name_receiver_dic=default_dic,
                account_number_dic=default_dic,
                sort_code_dic=default_dic,
                reference_dic=default_dic,
                email_sender_dic=default_dic,
                amount_dic=default_dic,
                email_receiver_dic=default_dic,
                add_fee=True,):
    
    return render_template('pay.html',
                           key=stripe_keys['publishable_key'],          
                           name_receiver=name_receiver_dic,
                           account_number=account_number_dic,
                           sort_code=sort_code_dic,
                           reference=reference_dic,
                           email_sender=email_sender_dic,
                           amount=amount_dic,
                           email_receiver=email_receiver_dic,
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
        email=values['email_sender'],
        card=request.form['stripeToken']
        )

    # create the charge on stripe's servers - this will charge the user's card
    success = False
    try:
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=price_in_pence(values['amount']), # required by stripe in pence
            currency='gbp',
            description=(values['pay_out'] 
                         + ' ' + values['name_receiver'] 
                         + ' ' + values['reference'])
            )
        success = True
    except stripe.CardError, e: # The card has been declined.
        success = False
        
    final_payment = add_and_modify_entries(values, customer.cards.data[0].name, success)
    final_payment = add_ID(final_payment, ID=0)
    print(final_payment)

    # Function to send emails for:
    # if provided, send an email to 'email_sender' (payer), notifying him that he was successfully charged
    #... try:
    # if provided, send an email to 'email_receiver', notifying him that he will get paid a certain sum 
    #... try:
    # send an email to me with whome to pay how much money (to receiver, then what my share is)
    #... try:

    if success:
        return redirect(url_for('success', amount=final_payment['amount']))
    else:
        return redirect(url_for('declined'))


#######################################
# /custom/<account_number>/<sort_code>/<name_receiver>/../../../
#######################################
@app.route('/custom/<account_number>/<sort_code>/<name_receiver>/')
@app.route('/custom/<account_number>/<sort_code>/<name_receiver>/<amount>/')
@app.route('/custom/<account_number>/<sort_code>/<name_receiver>/<amount>/<reference>/')
@app.route('/custom/<account_number>/<sort_code>/<name_receiver>/<amount>/<reference>/<email_receiver>/')
def custom(account_number, sort_code, name_receiver,
           amount='', reference='', email_receiver='', email_sender='',
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

        #special cases
        if values['reference']=='':
            arg_dic['reference_dic']['read_only'] = False
        if values['email_sender']=='':
            arg_dic['email_sender_dic']['read_only'] = False
        if values['amount']=='':
            arg_dic['amount_dic']['read_only'] = False
            arg_dic['amount_dic']['valid'] = True
        if values['amount']=='blank':
            arg_dic['amount_dic']['read_only'] = False
            arg_dic['amount_dic']['valid'] = True
            arg_dic['amount_dic']['value'] = ''
        return default_pay(**arg_dic)
    else:
        return charge(payment=values, add_fee=add_fee)


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
