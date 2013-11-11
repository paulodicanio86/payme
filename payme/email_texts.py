def return_text_success_receiver(**kwargs):
    text = '''Dear {name_receiver},\n
    You have successfully been paid {amount}{by}, which will reach your account 
    (Account number: {account_number}, Sort Code: {sort_code}, Reference: {reference})
    in 7 days.\n
    Thank you for using our service.
    '''
    by = ''
    if 'email_sender' in kwargs:
        by = ' by ' + kwargs.get('email_receiver')
    text = text.format(name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       amount=kwargs.get('amount', '[empty sum]'),
                       by=by,
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),                              
                       reference=kwargs.get('reference', '[reference]'))
    return text


def return_text_success_sender(**kwargs):
    text = '''
    You have successfully paid {amount}, which will reach the account of {name_receiver}
    (Account number: {account_number}, Sort Code: {sort_code}, Reference: {reference})
    in 7 days.\n
    Thank you for using our service.
    '''
    text = text.format(amount=kwargs.get('amount', '[empty sum]'),
                       name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),                              
                       reference=kwargs.get('reference', '[reference]'))
    return text


def return_text_failure_sender(**kwargs):
    text = '''
    Your payment of {amount} to the account of {name_receiver}
    (Account number: {account_number}, Sort Code: {sort_code}, Reference: {reference}) has just been declined.\n
    Please ensure you have entered the correct card information and/or try again with a different card.\n
    We hope it will work the next time.\n
    Thank you for using our service.
    '''
    text = text.format(amount=kwargs.get('amount', '[empty sum]'),
                       name_receiver=kwargs.get('name_receiver', '[receiver name]'),
                       account_number=kwargs.get('account_number', '[account number]'),
                       sort_code=kwargs.get('sort_code', '[sort code]'),                              
                       reference=kwargs.get('reference', '[reference]'))
    return text


def return_details(**kwargs):
    return str(kwargs)

