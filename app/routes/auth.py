from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app import mongo
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"LOGIN TRY: {username=}, {password=}")

        user = User.validate_login(mongo, username, password)
        print(f"USER FOUND: {user}")

        if user:
            login_user(user)
            print("LOGIN OK!")
            return redirect(url_for('admin.panel'))
        print("LOGIN FAIL!")
        flash('Invalid username or password', 'error')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))