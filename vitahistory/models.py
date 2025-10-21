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

from flask import current_app
from vitahistory import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    secondname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    image_user = db.Column(db.String(50), nullable=False, default='default.jpg')
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    speciality = db.Column(db.String(80), default='Specialty')

    persons = db.relationship('Person', backref='author', lazy=True)

    category = db.relationship('Category', backref='cat', lazy=True)

    def get_reset_token(self):
        # Generate a token to verify the password reset request.
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        """
        Verify if the provided token is valid.

        Args:
            token (str): The token to verify.

        Returns:
            User or None: The user corresponding to the token if valid, or None if invalid.
        """
        s = Serializer(current_app.config["SECRET_KEY"])
        try: 
            user_id = s.loads(token, max_age=300)["user_id"]
        except:
            return None

        return User.query.get(user_id)
        

    def __repr__(self):
        return f"User('{self.firstname}','{self.username}', '{self.email}')"


class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phonenumber = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(100))
    image_person = db.Column(db.String(50), nullable=False, default='default2.jpg')
    date_in = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    histories = db.relationship('History', backref='patient', lazy=True)

    def __repr__(self):
        return f"Person('{self.fullname}', '{self.email}', '{self.phonenumber}')"


class History(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_out = db.Column(db.DateTime, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

    def __repr__(self):
        return f"History('{self.title}', '{self.content}', '{self.date_out}')"


class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='Uncategorized')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __repr__(self):
        return f"Category('{self.name}', '{self.user_id}')"

