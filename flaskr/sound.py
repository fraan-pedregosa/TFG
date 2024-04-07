from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_sound_db
from flaskr.db import get_users_db

bp = Blueprint('sound', __name__)

@bp.route('/')
def index():
    sounds = get_sound_db()
    return render_template('sound/index.html', posts=posts)