from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email

class VacancyApplicationForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired()])
    message = TextAreaField('Сопроводительное письмо')
    resume = FileField('Резюме', validators=[DataRequired()])