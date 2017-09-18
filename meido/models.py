from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from secrets import token_hex
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import func
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

from meido.database import db
from meido.utils import extension_from_filename


user_project_subscription = db.Table(
    'user_project_subscription',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    commit = db.Column(db.String(64))
    commit_message = db.Column(db.Text)
    filename = db.Column(db.String(300))
    downloads = db.Column(db.Integer, nullable=False, default=0)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    __table_args__ = (
        UniqueConstraint('number', 'project_id', name='uq_build_number_project_id'),
    )

    def generate_filename(self, filename: str) -> str:
        """Generates a filename for the build file. Uses the original filename to get the
        extension.
        """
        ext = extension_from_filename(filename)
        filename = '{s.project.stub}-{s.number}{ext}'.format(s=self, ext=ext)
        self.filename = filename
        return filename


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    stub = db.Column(db.String(255), unique=True, nullable=False)
    color = db.Column(db.String(6))
    description = db.Column(db.Text)
    api_key = db.Column(db.String(64), unique=True)

    builds = db.relationship('Build', backref='project', lazy='dynamic')
    subscribed_users = db.relationship('User', secondary=user_project_subscription,
                                       backref=db.backref('projects', lazy='dynamic'))

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.stub = kwargs.get('stub', None)
        self.color = kwargs.get('color', None)
        self.description = kwargs.get('description', None)
        if not self.stub:
            self.stub = self.name.replace(' ', '-').lower()
        self.generate_api_key()

    def generate_api_key(self) -> str:
        """Generates a cryptographically strong 32-byte API key for the Project."""
        self.api_key = token_hex(32).upper()

    @property
    def last_updated(self) -> Optional[datetime]:
        """Returns a datetime object indicating when the latest build was uploaded. If the
        project has no builds, None is returned instead.
        """
        last_build = self.builds.order_by(Build.number.desc()).first()
        if last_build:
            return last_build.date
        return None


class User(db.Model, UserMixin):
    """User that has access to the management pages of Meido."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    date_changed_password = db.Column(db.DateTime, nullable=False)

    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.set_password(password)
        self.date_created = datetime.utcnow()

    def __repr__(self) -> str:
        """Returns a simple string representation of the given user."""
        return '<User %r>' % self.username

    def check_password(self, value: str) -> bool:
        """Check if a given password matches the user's saved password. Returns `True` if
        password is correct.
        """
        return check_password_hash(self.password_hash, value)

    def get_id(self) -> str:
        """Returns a Unicode representation of the user's primary key."""
        return '{}'.format(self.id)

    def set_password(self, password: str) -> None:
        """Generates a hash for the given password and sets it to user."""
        self.password_hash = generate_password_hash(password)
        self.date_changed_password = datetime.utcnow()
