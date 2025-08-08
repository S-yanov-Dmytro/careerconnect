from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=["GET", "POST"])
@login_required
def panel():
    # Обработка постов
    post_id = request.args.get("edit")
    editing = None
    if post_id:
        editing = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    if request.method == "POST" and request.form.get('form_type') != 'vacancy':
        title = request.form["title"]
        content = request.form["content"]
        description = content[:150] + '...' if len(content) > 150 else content
        pid = request.form.get("post_id")

        if pid:
            mongo.db.posts.update_one(
                {"_id": ObjectId(pid)},
                {"$set": {
                    "title": title,
                    "content": content,
                    "description": description,
                    "updated_at": datetime.utcnow()
                }}
            )
            flash('Пост обновлен успешно!', 'success')
        else:
            mongo.db.posts.insert_one({
                "title": title,
                "content": content,
                "description": description,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "views": 0
            })
            flash('Пост создан успешно!', 'success')
        return redirect(url_for('admin.panel'))

    # Обработка вакансий
    if request.method == 'POST' and request.form.get('form_type') == 'vacancy':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        conditions = request.form.get('conditions')
        vacancy_id = request.form.get('vacancy_id')

        vacancy_data = {
            "title": title,
            "description": description,
            "requirements": requirements,
            "conditions": conditions,
            "updated_at": datetime.utcnow()
        }

        if vacancy_id:
            mongo.db.vacancies.update_one(
                {"_id": ObjectId(vacancy_id)},
                {"$set": vacancy_data}
            )
            flash('Вакансия обновлена успешно!', 'success')
        else:
            vacancy_data["created_at"] = datetime.utcnow()
            vacancy_data["is_active"] = True
            mongo.db.vacancies.insert_one(vacancy_data)
            flash('Вакансия создана успешно!', 'success')
        return redirect(url_for('admin.panel'))

    # Получение данных для отображения
    posts = list(mongo.db.posts.find().sort("created_at", -1))
    vacancies = list(mongo.db.vacancies.find().sort("created_at", -1))
    editing_vacancy = None

    if 'edit_vacancy' in request.args:
        editing_vacancy = mongo.db.vacancies.find_one({"_id": ObjectId(request.args.get('edit_vacancy'))})

    return render_template(
        "admin.html",
        posts=posts,
        editing=editing,
        vacancies=vacancies,
        editing_vacancy=editing_vacancy
    )

@bp.route('/delete/<post_id>')
@login_required
def delete_post(post_id):
    mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
    flash('Пост удален успешно!', 'success')
    return redirect(url_for('admin.panel'))

@bp.route('/delete_vacancy/<vacancy_id>')
@login_required
def delete_vacancy(vacancy_id):
    mongo.db.vacancies.delete_one({"_id": ObjectId(vacancy_id)})
    flash('Вакансия удалена успешно!', 'success')
    return redirect(url_for('admin.panel'))


from app.models.forms import VacancyApplicationForm


@bp.route('/view_vacancy/<vacancy_id>')
def view_vacancy(vacancy_id):
    vacancy = mongo.db.vacancies.find_one({"_id": ObjectId(vacancy_id)})
    if not vacancy:
        abort(404)

    form = VacancyApplicationForm()
    return render_template('vacancy_detail.html', vacancy=vacancy, form=form)


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


@bp.route('/vacancies/<vacancy_id>/apply', methods=['POST'])
@login_required
def apply_vacancy(vacancy_id):
    # Получаем вакансию из БД
    vacancy = mongo.db.vacancies.find_one({"_id": ObjectId(vacancy_id)})
    if not vacancy:
        abort(404)

    # Получаем данные формы
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    resume = request.files.get('resume')

    # Настройки SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "sevostanovdima705@gmail.com"  # Замените на ваш email
    smtp_password = "vhda sfme zxms oamc"  # Пароль приложения

    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = smtp_username
    msg['Subject'] = f"Новая заявка на вакансию: {vacancy['title']}"  # Используем словарный доступ

    body = f"""
    Вакансия: {vacancy['title']}
    Имя: {full_name}
    Email: {email}
    Телефон: {phone}
    Сообщение: {message}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Добавляем вложение
    if resume:
        part = MIMEApplication(resume.read(), Name=resume.filename)
        part['Content-Disposition'] = f'attachment; filename="{resume.filename}"'
        msg.attach(part)

    try:
        # Отправляем email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        flash('Ваша заявка успешно отправлена!', 'success')
    except Exception as e:
        flash(f'Ошибка при отправке: {str(e)}', 'error')

    return redirect(url_for('admin.view_vacancy', vacancy_id=vacancy_id))