from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField(
        label='email',
        validators=[
            DataRequired(message='The e-mail field is required'),
        ]
    )

    password = PasswordField(
        label='password',
        validators=[
            DataRequired(message='The password field is required'),
        ]
    )
