import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_users_db

from bson import ObjectId

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
        else:
            user = get_users_db().find_one({'email': email})
            if user is not None:
                error = 'Este correo electrónico ya está registrado.'

        if error is None:
            try:
                collection_users = get_users_db()
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
        user = get_users_db().find_one({'email': email})
        if user is None:
            error = 'El correo electrónico no existe.'
        elif not check_password_hash(user['password'], password):
            error = 'La contraseña es incorrecta.'
        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])  # Convert ObjectId to string before storing in session return redirect(url_for('index'))
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')

        
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Convert the string back to ObjectId before fetching the user from the database
        g.user = get_users_db().find_one({'_id': ObjectId(user_id)})

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
