import re, string, datetime
from wtforms import ValidationError

from payme import (rate, card_usage_fee, threshold, fixed_fee)


def is_number(input):
    try:
        float(input)
        return True
    except ValueError:
        return False

def is_integer_string(input_string):
    return (isinstance(input_string, basestring)
            and input_string.isdigit())

def matches_reg_ex(input_string, reg_ex):
    """
    Checks if input_string is string or unicode object
    and if it matches the regular expression.
    Empty strings return False.
    """
    return (isinstance(input_string, basestring)
            and re.match(reg_ex, input_string) != None)

def valid_name(name):
    """
    Checks if account holder name is valid and a string.
    Valid: 1-18 characters long
    """
    reg_ex = '^[A-Za-z0-9. _!,&-]+$'
    length = 18
    return (matches_reg_ex(name, reg_ex)
            and len(name)<=length)

def valid_email(email):
    """
    Checks if email is valid and a string.
    """
    reg_ex = '[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}'
    if (isinstance(email, basestring)
        and len(email)==0):
        return True
    else:
        return matches_reg_ex(email, reg_ex)
    
def valid_reference(reference):
    """
    Checks if reference is valid and a string.
    Valid: 0-18 characters long
    """
    if (isinstance(reference, basestring)
        and len(reference)==0):
        return True
    else:
        return valid_name(reference)

def valid_account_number(account_number):
    """
    Checks if account_number is valid and a string.
    Valid: 12345678
    """
    length = 8
    return (is_integer_string(account_number)
            and len(account_number)==length)

def valid_sort_code(sort_code):
    """
    Checks if sort_code is valid and a string.
    Valid: 12-34-56
    """
    reg_ex = '[0-9][0-9][-][0-9][0-9][-][0-9][0-9]'
    length = 8
    return (matches_reg_ex(sort_code, reg_ex)
            and len(sort_code)==length)

def convert_sort_code(sort_code):
    """
    Converts common mistakes in sort code to correct format
    """
    # 12 34.56 -> 12-34-56, 12_34:45 -> 12-34-56, etc.
    reg_ex = '[0-9][0-9][ _:.-][0-9][0-9][ _:.-][0-9][0-9]'
    length = 8
    if (matches_reg_ex(sort_code, reg_ex)
        and len(sort_code)==length):
        return (sort_code[0:2] + '-'
                + sort_code[3:5] + '-'
                + sort_code[6:8])
    # 123456 -> 12-34-56
    length = 6
    if (is_integer_string(sort_code)
        and len(sort_code)==length):
        return (sort_code[0:2] + '-'
                + sort_code[2:4] + '-'
                + sort_code[4:6])
    return sort_code

def convert_white_space_in_link(input_string):
    input_string = string.replace(input_string, ' ', '%20')
    return input_string

def convert_special_characters(input_string):
    input_string = string.replace(input_string, '"', '_')
    input_string = string.replace(input_string, "'", "_")
    input_string = string.replace(input_string, '#', '_')
    input_string = string.replace(input_string, '<', '_')
    input_string = string.replace(input_string, '>', '_')
    input_string = string.replace(input_string, '\t', '_')
    input_string = string.replace(input_string, '\n', '_')
    input_string = string.replace(input_string, '/', '_')
    input_string = string.replace(input_string, '\\', '_')
    return input_string

def convert_price(price):
    """
    Convert ,->.
    """
    return string.replace(price, ',', '.')

def valid_fee(value):
    """
    Validate fee
    Input/Output are strings
    Valid: 129.99
    """
    reg_ex = '^[0-9]+[.][0-9][0-9]$'
    return (is_number(value)
            and matches_reg_ex(value, reg_ex)
            and float(value)>0.00)

def valid_price(value):
    """
    Validate price and check that price is >0.50p
    Input/Output are strings
    Valid: 129.99
    """
    return (valid_fee(value)
            and float(value)>3.00)

def price_in_pence(price):
    """
    Input/Output are strings
    129.99 -> 12999
    """
    if valid_price(price):
        return str(int(float(price) * 100.0))

def two_digit_string(value):
    if type(value) == str or type(value) == unicode:
        value = float(value)
    return '{0:.2f}'.format(value)

def price_in_pound(price):
    """
    Input/Output are strings
    123 -> 1.23
    """
    if is_integer_string(price):
        return two_digit_string(int(price) / 100.0)


#######################################
# combining the above functions in two
#######################################
def convert_entries(entry, value):
    if entry=='name':
        return convert_special_characters(value)
    elif entry=='sort_code':
        return convert_sort_code(value)
    elif entry=='reference':
        return convert_special_characters(value)
    elif entry=='amount':
        return convert_price(value)
    else:
        return value

def validate_entries(entry, value):
    if entry=='name_receiver':
        return valid_name(value) 
    elif entry=='account_number':
        return valid_account_number(value)
    elif entry=='sort_code':
        return valid_sort_code(value)
    elif entry=='reference':
        return valid_reference(value)
    elif entry=='email_sender':
        return valid_email(value)
    elif entry=='email_receiver':
        return valid_email(value)
    elif entry=='amount':
        return valid_price(value)
    else:
        return False

def get_boolean(value):
    if str(value)=='True':
        return True
    else:
        return False


#######################################
# wtforms custom validators
#######################################
class Sort_Code(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid sort code'
        self.message = message

    def __call__(self, form, field):
        value = field.data
        if not valid_sort_code(value):
            raise ValidationError(self.message)

class Account_Number(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid account number'
        self.message = message

    def __call__(self, form, field):
        value = field.data
        if not valid_account_number(value):
            raise ValidationError(self.message)

class Amount(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid price'
        self.message = message

    def __call__(self, form, field):
        value = field.data
        if not valid_price(value):
            raise ValidationError(self.message)


#######################################
# calculating the fee
#######################################
def get_fee(value, inverse=False,
            rate=rate, card_usage_fee=card_usage_fee,
            threshold=threshold, fixed_fee=fixed_fee):
    """
    Input/Output are strings
    """
    rate = rate / 100.0 # in decimal
    value = float(value)
    fixed_fee = two_digit_string(fixed_fee)

    # if value is below threshold return fixed fee
    if (value <= threshold
        and valid_fee(fixed_fee)):
        return fixed_fee

    # calculate fee
    fee = value * rate + card_usage_fee
    if inverse:
        fee /= (1.0 - rate)

    # return fee as correct string
    fee = two_digit_string(fee)
    if valid_fee(fee):
        return fee
    
def get_fee_stripe(value, inverse=False):
    """
    Input/Output are strings
    """
    return get_fee(value, inverse, 2.4, 0.20, 0.0)


#######################################
# calculate and add field to payment
#######################################
def add_and_modify_entries(values, name_sender, success):
    # add string field(s)
    values['name_sender'] = name_sender
    values['success'] = success
    values['datetime'] = datetime.datetime.now().isoformat()
    # convert certain fields to floats
    values['pay_out'] = float(values['pay_out']) # this needs to be paid out to receiver
    values['charged'] = float(values['amount']) # this is what was charged from cc card
    values['fee'] = float(values['fee']) # this is my fee
    values['fee_stripe'] = float(values['fee_stripe']) # this is stripe's fee
    # calculate new fields
    values['paid_in'] = values['charged'] - values['fee_stripe'] # this is what will reach my account
    values['profit'] = values['paid_in'] - values['pay_out'] # this is what I can keep
    values['profit2'] = values['fee'] - values['fee_stripe'] # this should be the same - (better, as usually exactly 2 digits)
    values['check_sum'] = values['profit'] - values['profit2'] # and this should be 0.0

    return values

def add_ID(values, ID):
    values['ID'] = ID
    return values
