# initialisation de l'application flask 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from app.attacks.phishing import phishing_attack


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), 
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    app.register_blueprint(phishing_attack, url_prefix='/phishing')
    
    return app