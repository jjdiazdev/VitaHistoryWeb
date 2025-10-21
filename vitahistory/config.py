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

import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_PASS = os.environ.get("EMAIL_PASS")
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(
        os.environ.get('MYSQL_USER'),
        os.environ.get('MYSQL_PASSWORD'),
        os.environ.get('MYSQL_HOST'),
        os.environ.get('MYSQL_DATABASE')
        )

