from __future__ import division, print_function, absolute_import

import os
import stripe
from flask import (render_template, request, send_from_directory, redirect,
                   url_for)

from payme import app, stripe_keys, company, domain, variable_names
from payme.validation_functions import *
from payme.email import send_emails
from payme.forms import GeneratorForm


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


    # Connecting with strip and charging if successfull
    success = False
    name_sender = ''
    try:
        # make the customer
        customer = stripe.Customer.create(
            email=values['email_sender'],
            card=request.form['stripeToken']
            )

        # create the charge on stripe's servers - this will charge the user's card
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=price_in_pence(values['amount']), # required by stripe in pence
            currency='gbp',
            description=(values['pay_out'] 
                         + ' ' + values['name_receiver'] 
                         + ' ' + values['reference'])
            )
        success = True
        name_sender = customer.cards.data[0].name
    except stripe.CardError, e: # The card has been declined.
        success = False
        name_sender = '[card was declined, no name]'

    # add/modify final_payment dictionary
    final_payment = add_and_modify_entries(values, name_sender, success)
    final_payment = add_ID(final_payment, ID=0)
    #print(final_payment)

    # send emails, depending on success/failure
    send_emails(success, final_payment)

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
        blanks = ['', '%20', ' ', 'empty']
        if values['reference'] in blanks:
            arg_dic['reference_dic']['read_only'] = False
            arg_dic['reference_dic']['value'] = ''
        if values['email_sender'] in blanks:
            arg_dic['email_sender_dic']['read_only'] = False
            arg_dic['email_sender_dic']['value'] = ''
        if values['amount'] in blanks:
            arg_dic['amount_dic']['read_only'] = False
            arg_dic['amount_dic']['valid'] = True
            arg_dic['amount_dic']['value'] = ''

        return default_pay(**arg_dic)
    else:
        #special case
        if values['reference'] == 'empty':
            values['reference'] = ''
            
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
# /generate_payment/
#######################################
@app.route('/generate_payment/', methods=['GET', 'POST'])
def generate_payment(company=company):
    # Generate forms for link generation
    form = GeneratorForm()

    if form.validate_on_submit():
        # Form is valid, lets get the data
        name_receiver = form.name_receiver.data
        email_receiver = form.email_receiver.data
        amount = form.amount.data
        amount_paid_out = ''
        if amount != u'':
            fee = get_fee(amount, False)
            #Here improve, s.t. the price looks like 150.00 (not 150.0)
            amount_paid_out = str(float(amount) - float(fee))  
           
        # Construct the link paths
        rel_link = '/custom/'
        rel_link += form.account_number.data + '/'
        rel_link += form.sort_code.data + '/'
        rel_link += form.name_receiver.data + '/'

        # Add the optional statements in a special way
        def optional_add(rel_link, to_add):
            if to_add == u'':
                rel_link += 'empty/'
            else:
                rel_link += to_add + '/'
            return rel_link

        rel_link = optional_add(rel_link, form.amount.data)
        rel_link = optional_add(rel_link, form.reference.data)
        rel_link = optional_add(rel_link, form.email_receiver.data)
        
        # Strip empty cells at the end of link paths
        def strip_end(link, suffix):
            while link.endswith(suffix):
                link = link[:-len(suffix)]
            return link
        rel_link = strip_end(rel_link, 'empty/')
        abs_link = 'http://' + domain + rel_link
        
        return render_template('custom_link.html',
                               name_receiver=name_receiver,
                               amount_charged=amount,
                               amount_paid_out=amount_paid_out,
                               email_receiver=email_receiver,
                               rel_link=rel_link,
                               abs_link=abs_link,
                               company=company)
    else:
        # Forms not validated, resubmit
        return render_template('generate_payment.html',
                               form=form,
                               company=company)





#######################################
# /about/
#######################################
@app.route('/about/')
def about(company=company):
    return render_template('about.html',
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
