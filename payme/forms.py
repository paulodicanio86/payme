from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Length, Optional, Email

from validation_functions import Sort_Code, Account_Number, Amount
from validation_functions import convert_sort_code, convert_price

class SortCodeField(StringField):
    def _value(self):
        if self.data:
            return convert_sort_code(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = convert_sort_code(valuelist[0])
        else:
            self.data = []


class AmountField(StringField):
    def _value(self):
        if self.data:
            return convert_price(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = convert_price(valuelist[0])
        else:
            self.data = []


class GeneratorForm(Form):
    name_receiver = StringField('Your Name', validators=[InputRequired(), Length(max=18)])
    account_number = StringField('Your Account No.', validators=[InputRequired(), Account_Number()])
    sort_code = SortCodeField('Your Sort Code', validators=[InputRequired(), Sort_Code()])
    amount = AmountField('Amount', validators=[Optional(), Amount()])
    reference = StringField('Reference', validators=[Optional(), Length(max=18)])
    email_receiver = StringField('Your E-Mail', validators=[Optional(), Email()])
