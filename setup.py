from setuptools import find_packages, setup

dev_requirements = [
    'factory-boy==2.8.1',
    'nose2==0.6.5',
]
requirements = [
    'Flask-DebugToolbar==0.10.1',
    'Flask-Login==0.4.0',
    'flask-migrate==2.1.1',
    'Flask-Restful==0.3.6',
    'Flask-Script==2.0.5',
    'Flask-SQLAlchemy==2.2',
    'Flask-WTF==0.14.2',
    'Flask==0.12.2',
    'humanize==0.5.1',
    'itsdangerous==0.24',
    'psycopg2==2.7.2',
    'raven==6.1.0',
    'SQLAlchemy==1.1.11',
    'WTForms==2.1',
]

setup(
    name='Meido',
    version='1.0.0',
    description='Build distribution web application',
    url='https://github.com/arttuperala/Meido',
    author='Arttu Perälä',
    author_email='arttu@perala.me',
    license='Apache2',
    packages=['meido'],
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
)
