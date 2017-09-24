from flask_wtf import FlaskForm
from re import match
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from meido.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired('Username is required.')
    ])
    password = PasswordField('Password', validators=[Optional()])

    def validate(self) -> bool:
        """Performs user and password validation. Returns True if login is successful."""
        if not super().validate():
            return False

        # Does the user exist
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        # Does given password match user's password
        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True


class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()], description='Required.')
    stub = StringField('Stub', validators=[Optional()],
                       description='Used to form URLs for the project. Typically the '
                                   'project name in lower-case and with spaces replaced '
                                   'by dashes. Leave blank for automatic.')
    color = StringField('Color code',
                        description='Hexadecimal color code for the project used for '
                                    'theming the pages. Optional.')
    description = TextAreaField('Description')
    github_shorthand = StringField(
        'Github shorthand',
        description='Github owner and repo names separated by a slash. '
                    'For example: arttuperala/Meido'
    )

    def validate_color(self, field):
        """Validates that the color field is a valid hexadecimal value between 0 and 6
        characters inclusive. If validation is successful, turns string into lowercase.
        """
        if match(r'^[A-Fa-f0-9]{0,6}$', field.data):
            field.data = field.data.lower()
        else:
            raise ValidationError('Field is not a valid hexadecimal color code.')
