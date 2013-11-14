from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class GeneratorForm(Form):
    name_receiver = StringField('Account Holder Name', validators=[DataRequired()])
    reference = StringField('Reference', validators=[DataRequired()])
