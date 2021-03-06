##from mongokit import Document

##class Payment(Document):
class Payment():
    structure = {
        'pay_out': float,
        'check_sum': float,
        'fee': float,
        'name_sender': unicode,
        'name_receiver': unicode,
        'reference': unicode,
        'profit': float,
        'fee_stripe': float,
        'success': bool,
        'datetime': unicode,
        'email_sender': unicode,
        'amount': unicode,
        'account_number': unicode,
        'paid_in': float,
        'sort_code': unicode,
        'profit2': float,
        'ID': int,
        'email_receiver': unicode,
        'charged': float,
        'other_data': dict}
    required_fields = [
        'pay_out',
        'check_sum',
        'fee',
        'name_sender',
        'name_receiver',
        'reference',
        'profit',
        'fee_stripe',
        'success',
        'datetime',
        'email_sender',
        'amount',
        'account_number',
        'paid_in',
        'sort_code',
        'profit2',
        'ID',
        'email_receiver',
        'charged',
        'other_data'
        ]
