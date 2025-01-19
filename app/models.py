# Modèle de la Base de Données avec SQLAlchemy

from app import db

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack_type = db.Column(db.String(50), nullable=False)
    target_ip = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(200), nullable= False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
def __init__(self, attack_type, target_ip, result):
    self.attack_type = attack_type
    self.target_ip = target_ip
    self.result = result