# VitaHistory - A CRM system for healthcare professionals
# Copyright (C) 2025 Jorman Diaz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Blueprint, render_template, request, url_for, flash, redirect
from flask_login import login_required, current_user
from vitahistory.models import User
from vitahistory import db
from vitahistory.tools import save_picture, get_current_year

index = Blueprint('index', __name__, url_prefix='/index')


@index.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index.start'))

    current_year = get_current_year()

    return render_template('index/home.html', current_year=current_year)


@index.route("/start")
@login_required
def start():



    return render_template('index/start.html')

@index.route("/start/development")
@login_required
def work_in_progress():


    flash('Módulo en proceso de desarrollo', 'info')

    return render_template('index/start.html')

@index.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == "POST":
        firstname = request.form["firstname"]
        secondname = request.form["secondname"]
        username = request.form["username"]
        speciality = request.form["speciality"]

        if request.files["picture"]:
            user_picture = request.files["picture"]
            picture_file = save_picture(user_picture)

            current_user.image_user = picture_file

        error = None

        if username != current_user.username:
            user_username = User.query.filter_by(username=username).first()
            if isinstance(user_username, User):
                error = "Este nombre de usuario ya existe, por favor elige otro"
            else:
                current_user.username = username
        

        if error is None:
            current_user.firstname = firstname
            current_user.secondname = secondname
            current_user.speciality = speciality


            db.session.commit()

            flash("Información actualizada exitosamente", "success")
            return redirect(url_for('index.account'))

        if error is not None:
            flash(error)


    image_user = url_for('static', filename='image/' + current_user.image_user)
    return render_template('index/account.html', image_user=image_user)
