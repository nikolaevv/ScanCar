import os

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = 'photos'
token = '00978ffb1ced950ecf1af6dc69351fa1'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False