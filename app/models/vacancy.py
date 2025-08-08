from app import mongo
from bson.objectid import ObjectId
from datetime import datetime


from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email

class ApplicationForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired()])
    message = TextAreaField('Сопроводительное письмо')
    resume = FileField('Резюме', validators=[DataRequired()])



class Vacancy:
    @staticmethod
    def create(title, description, requirements, conditions):
        vacancy = {
            'title': title,
            'description': description,
            'requirements': requirements,
            'conditions': conditions,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        return mongo.db.vacancies.insert_one(vacancy)

    @staticmethod
    def get_all():
        return list(mongo.db.vacancies.find().sort('created_at', -1))

    @staticmethod
    def get_by_id(vacancy_id):
        return mongo.db.vacancies.find_one({'_id': vacancy_id})

    @staticmethod
    def update(vacancy_id, title, description, requirements, conditions):
        return mongo.db.vacancies.update_one(
            {'_id': vacancy_id},
            {'$set': {
                'title': title,
                'description': description,
                'requirements': requirements,
                'conditions': conditions,
                'updated_at': datetime.utcnow()
            }}
        )

    @staticmethod
    def delete(vacancy_id):
        return mongo.db.vacancies.delete_one({'_id': vacancy_id})