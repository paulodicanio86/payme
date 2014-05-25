from payme.validation_functions import two_digit_string
from payme import currency

def return_text_success_receiver(**kwargs):
    text = '''
Hi {name_receiver},
You have successfully been paid {currency}{pay_out}{by}, which will reach your account 
(Account number: {account_number}, Sort Code: {sort_code}{reference}) within approximately 7 days.

Thank you for using NicerPay.
    '''

    by = ''
    if kwargs.get('email_sender', '') != '':
        by = ' by ' + kwargs.get('email_sender')
        
    reference = ''
    if kwargs.get('reference', '[reference]') != '':
        reference = ', Reference: ' + kwargs.get('reference', '[reference]')
        
    text = text.format(name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       pay_out=two_digit_string(kwargs.get('pay_out', '[empty sum]')),
                       by=by,
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),
                       currency=currency,
                       reference=reference)
    return text


def return_text_success_sender(**kwargs):
    text = '''
Hi,
Your card has been successfully charged {currency}{charged}, of which {currency}{pay_out} will reach the account of {name_receiver}
(Account number: {account_number}, Sort Code: {sort_code}{reference}) within approximately 7 days.

Thank you for using NicerPay.
    '''
    
    reference = ''
    if kwargs.get('reference', '[reference]') != '':
        reference = ', Reference: ' + kwargs.get('reference', '[reference]')
        
    text = text.format(charged=two_digit_string(kwargs.get('charged', '[empty sum]')),
                       pay_out=two_digit_string(kwargs.get('pay_out', '[empty sum]')),
                       name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),
                       currency=currency,
                       reference=reference)
    return text


def return_text_failure_sender(**kwargs):
    text = '''
Hi,
Your payment of {currency}{pay_out} to the account of {name_receiver}
(Account number: {account_number}, Sort Code: {sort_code}{reference}) has just been declined.
Please ensure you have entered the correct card information and/or try again with a different card.
We hope it will work the next time.

Thank you for using NicerPay.
    '''

    reference = ''
    if kwargs.get('reference', '[reference]') != '':
        reference = ', Reference: ' + kwargs.get('reference', '[reference]')
    
    text = text.format(pay_out=two_digit_string(kwargs.get('pay_out', '[empty sum]')),
                       name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),
                       currency=currency,
                       reference=reference)
    return text


def return_details(**kwargs):
    text = '''date: {datetime}
paid-in: {paid_in}

pay-out: {pay_out}
name: {name_receiver}
account-number: {account_number}
sort-ode: {sort_code}
reference: {reference}

keep: {profit2}
stripe-fee: {fee_stripe}
check-sum: {check_sum}

'''

    datetime=kwargs.get('datetime')

    text = text.format(datetime=datetime,
                       paid_in=two_digit_string(kwargs.get('paid_in')),
                       pay_out=two_digit_string(kwargs.get('pay_out')),
                       name_receiver=kwargs.get('name_receiver'),
                       account_number=kwargs.get('account_number'),
                       sort_code=kwargs.get('sort_code'),
                       reference=kwargs.get('reference'),
                       profit2=kwargs.get('profit2'),
                       fee_stripe=kwargs.get('fee_stripe'),
                       check_sum=kwargs.get('check_sum'))
    
    return text+str(kwargs)

    
