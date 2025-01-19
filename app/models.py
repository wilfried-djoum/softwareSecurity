from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack_type = db.Column(db.String(50), nullable=False)
    target_ip = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(500), nullable=True)
    
    # Colonnes spécifiques à l'attaque DoS
    successful_responses = db.Column(db.Integer, default=0)
    error_responses = db.Column(db.Integer, default=0)
    timeouts = db.Column(db.Integer, default=0)
    errors = db.Column(db.Integer, default=0)
    average_latency = db.Column(db.Float, default=0.0)

    def __init__(self, attack_type, target_ip, result, successful_responses=0, error_responses=0, timeouts=0, errors=0, average_latency=0.0):
        self.attack_type = attack_type
        self.target_ip = target_ip
        self.result = result
        self.successful_responses = successful_responses
        self.error_responses = error_responses
        self.timeouts = timeouts
        self.errors = errors
        self.average_latency = average_latency
