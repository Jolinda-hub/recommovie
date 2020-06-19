from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class SignupForm(FlaskForm):
    name = StringField(
        label='name',
        validators=[
            Length(
                min=3,
                message='The name field must be at least 6 characters long.'
            ),
            DataRequired(
                message='The name field is required'
            )
        ]
    )

    email = StringField(
        label='email',
        validators=[
            Length(
                min=6,
                message='The email field must be at least 6 characters long.'
            ),
            DataRequired(
                message='The e-mail field is required'
            ),
            Email(
                message='Please enter a valid email'
            )
        ]
    )

    password = PasswordField(
        label='password',
        validators=[
            DataRequired(
                message='The password field is required'
            ),
            Length(
                min=6,
                message='Please select a stronger password'
            )
        ],
    )

    confirm = PasswordField(
        label='confirm your password',
        validators=[
            DataRequired(
                'Please confirm your password'
            ),
            EqualTo(
                'password',
                message='Passwords must match'
            )
        ]
    )
