import re, string


def is_integer_string(input_string):
    return (isinstance(input_string, basestring)
            and input_string.isdigit())

def matches_reg_ex(input_string, reg_ex):
    """
    Checks if input_string is string or unicode object
    and if it matches the regular expression.
    Empty strings return False.
    """
    return (isinstance(input_string, basestring) and
            re.match(reg_ex, input_string) != None)

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
    reg_ex = "[0-9][0-9][-][0-9][0-9][-][0-9][0-9]"
    length = 8
    return (matches_reg_ex(sort_code, reg_ex)
            and len(sort_code)==length)

def alter_sort_code(sort_code):
    """
    Transforms common mistakes in sort code to correct format
    """
    # 12 34.56 -> 12-34-56, 12_34:45 -> 12-34-56, etc.
    reg_ex = "[0-9][0-9][ _:.-][0-9][0-9][ _:.-][0-9][0-9]"
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

def convert_whitespace(input_string):
    return string.replace(input_string, ' ', '_')

def convert_comma(input_string):
    return string.replace(input_string, ',', '.')

def valid_price(price):
    """
    Valid: 129.99
    """
    reg_ex = "^[0-9]+[.][0-9][0-9]$"
    return matches_reg_ex(price, reg_ex)

def into_pence(price):
    """
    129.99 -> 12999
    """
    if valid_price(price):
        return str(int(float(price) * 100.0))

def into_pound(price):
    """
    123 -> 1.23
    """
    if is_integer_string(price):
        return str(int(price) / 100.0)
        









