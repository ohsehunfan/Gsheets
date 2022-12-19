from wtforms.fields.datetime import  DateField
from wtforms import validators, SubmitField, SelectField, StringField, PasswordField
from flask_wtf import FlaskForm

class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=(validators.DataRequired(),))
    password = PasswordField('Password', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')