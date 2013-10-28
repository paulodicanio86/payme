import re, string
from payme import (rate, card_usage_fee, threshold, fixed_fee)


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
    reg_ex = '^[A-Za-z0-9 _-]+$'
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

def convert_special_characters(input_string):
    #input_string = string.replace(input_string, ' ', '_')
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
    return (matches_reg_ex(value, reg_ex)
            and float(value)>0.00)

def valid_price(value):
    """
    Validate price and check that price is >0.50p
    Input/Output are strings
    Valid: 129.99
    """
    return (valid_fee(value)
            and float(value)>0.50)

def price_in_pence(price):
    """
    Input/Output are strings
    129.99 -> 12999
    """
    if valid_price(price):
        return str(int(float(price) * 100.0))

def two_digit_string(value):
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
def convert_entries(values):
    values['name'] = convert_special_characters(values['name'])
    values['sort_code'] = convert_sort_code(values['sort_code'])
    values['reference'] = convert_special_characters(values['reference'])
    values['amount'] = convert_price(values['amount'])
    return values

def validate_entries(valids, values):
    valids['name'] = valid_name(values['name']) 
    valids['account_number'] = valid_account_number(values['account_number'])
    valids['sort_code'] = valid_sort_code(values['sort_code'])
    valids['reference'] = valid_reference(values['reference'])
    valids['email'] = valid_email(values['email'])
    valids['amount'] = valid_price(values['amount'])
    return valids


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
