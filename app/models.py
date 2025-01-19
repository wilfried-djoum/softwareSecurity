from app import db

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack_type = db.Column(db.String(50), nullable=False)
    target_ip = db.Column(db.String(50), nullable=False)
    result = db.Column(db.Text, nullable=False)  # Stocker du JSON sous forme de texte
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
