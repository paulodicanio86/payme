from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Length, Optional, Email

from validation_functions import Sort_Code, Account_Number, Amount


class GeneratorForm(Form):
    name_receiver = StringField('Account Holder Name', validators=[InputRequired(), Length(max=18)])
    account_number = StringField('Account Number', validators=[InputRequired(), Account_Number()])
    sort_code = StringField('Sort Code', validators=[InputRequired(), Sort_Code()])
    amount = StringField('Amount', validators=[Optional(), Amount()])
    reference = StringField('Reference', validators=[Optional(), Length(max=18)])
    email_receiver = StringField('Account Holder E-Mail', validators=[Optional(), Email()])
