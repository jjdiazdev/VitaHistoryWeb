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

from flask import (
        Blueprint,
        render_template,
        )

error = Blueprint("error", __name__, url_prefix='/error')


@error.app_errorhandler(404)
def error_404(error):
    return render_template('error/404.html'), 404


@error.app_errorhandler(403)
def error_403(error):
    return render_template('error/403.html'), 403


@error.app_errorhandler(500)
def error_500(error):
    return render_template('error/500.html'), 500
