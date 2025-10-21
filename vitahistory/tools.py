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

from flask import url_for, current_app
from datetime import datetime
import secrets
import os
from PIL import Image
import smtplib
from email.message import EmailMessage


def get_current_year():
    return datetime.now().year


def get_current_time():
    return datetime.now()


def save_picture(user_picture):
    # Genera un nombre único para la imagen usando tokens aleatorios
    random_hex = secrets.token_hex(8)

    _, f_ext = os.path.splitext(user_picture.filename)
    picture_filename = random_hex + f_ext

    # Construye el ruta completa donde se guardará la imagen
    picture_path = os.path.join(current_app.root_path, 'static/image', picture_filename)

    # Redimensiona la imagen a una resolución de 100x100 pixels
    output_size = (100, 100)
    new_image = Image.open(user_picture)
    new_image.thumbnail(output_size)

    # Guarda la imagen en el directorio especificado
    new_image.save(picture_path)

    # Devuelve el nombre del archivo guardado para su uso posterior
    return picture_filename


def send_reset_email(user, to_email, to_username):
    """
    Esta función envía un correo electrónico con un enlace de reseteo de contraseña al usuario.

    Args:
    user (User): El objeto User que contiene la información del usuario.
    to_email (str): La dirección de correo electrónico al que se enviará el correo.
    to_username (str): El nombre de usuario del usuario.
    """

    EMAIL_ADDRESS = current_app.config["EMAIL_USER"]
    EMAIL_PASSWORD = current_app.config["EMAIL_PASS"]

    #obtenemos el token del usuario a partir del método definido en el modelo
    token = user.get_reset_token()

    msg = EmailMessage()
    msg['Subject'] = 'Información de reseteo de contraseña en VitaHistory'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    msg.set_content("""
    Mensaje de resteo de contraseña para el usuario: {}
    Correo electrónico registrado en la plataforma: {}
    Para resetear la contraseña, visita el siguiente link: {}. 
    Si no hiciste la solicitud de este mensaje, solo ignoralo y no habrá ningún cambio en tu usuario de VitaHistory
    """.format(to_username, to_email, url_for('auth.reset_final', token=token, _external=True))
    )

    msg.add_alternative("""\
    <!DOCTYPE html>
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="width: 80%; margin: 20px auto; border: 1px solid #ddd; padding: 20px;">
                <div style="background-color: #f0f8ff; padding: 10px; text-align: center;">
                    <h1 style="color: #5BC058;">Recuperación de Contraseña VitaHistory</h1>
                </div>
                <div style="margin-top: 20px;">
                    <p>Hola {},</p>
                    <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                    <p>Tu correo electrónico registrado es: {}.</p>
                    <p>Para restablecer tu contraseña, haz clic en el siguiente enlace:</p>
                    <p><a href="{}" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
                    <p style="margin-top: 20px; font-size: 0.9em; color: #777;">Si no solicitaste este cambio, puedes ignorar este correo. Tu cuenta permanecerá segura.</p>
                </div>
            </div>
        </body>
    </html>
    """.format(to_username, to_email, url_for('auth.reset_final', token=token, _external=True)), subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
