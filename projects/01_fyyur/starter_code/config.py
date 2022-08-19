import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
DATABASE_NAME = 'fyyur'
username = 'postgres'
password = ''
url = 'localhost:5432'
SQLALCHEMY_DATABASE_URI = f'postgresql://{username}@{url}/{DATABASE_NAME}'
