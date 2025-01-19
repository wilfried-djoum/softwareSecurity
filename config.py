import os

class Config:
    SECRET_KEY = os.getenv('primal', 'mysecretkey')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "app", "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
