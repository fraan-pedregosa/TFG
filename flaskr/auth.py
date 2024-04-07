import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error = None

        if not name:
            error = 'Por favor ingrese su nombre.'
        elif not email:
            error = 'Por favor ingrese su correo electrónico.'
        elif not password:
            error = 'Por favor ingrese una contraseña.'
        elif not confirm_password:
            error = 'Por favor confirme la contraseña.'
        elif password != confirm_password:
            error = 'Las contraseñas no coinciden.'

        if error is None:
            try:
                collection_users = get_db().users
                collection_users.insert_one({
                    'name': name,
                    'email': email,
                    'password': generate_password_hash(password),
                    'isAdmin': False
                })
            except db.IntegrityError:
                error = f'El correo electrónico:  {email} ya está registrado.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = get_db().user.find_one({'email': email})
        if user is None:
            error = 'El correo electrónico no existe.'
        elif not check_password_hash(user['password'], password):
            error = 'La contraseña es incorrecta.'
        if error is None:
            session.clear()
            session['user_id'] = user['_id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().user.find_one({'_id': user_id})

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
