import asyncio
import json
import os
import time
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import Attack
from app import db
from app.attacks import sql_injection_attack, error_handling_attack, vulnerable_library_attack, xss_attack, xxe_attack
from app.attacks import ddos_attack
from app.attacks.csrf import csrf_vulnerability_scan
from app.attacks.html_injection import html_injection

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/attack', methods=['POST'])
def attack():
    # Récupérer les données de la requête
    attack_type = request.json['attackType']
    target_ip = request.json['targetIP']
    results = {}

    # Simulation du temps d'exécution (3 secondes)
    time.sleep(3)

    # Exécuter l'attaque correspondante
    if attack_type == "sqlInjection":
        result_message = asyncio.run(sql_injection_attack(target_ip))
    elif attack_type == "xss":
        result_message = asyncio.run(xss_attack(target_ip))
    elif attack_type == "xxe":
        result_message = asyncio.run(xxe_attack(target_ip))
    elif attack_type == "vulnerableLibrary":
        result_message = asyncio.run(vulnerable_library_attack(target_ip))
    elif attack_type == "errorhandling":
        result_message = error_handling_attack(target_ip)
    elif attack_type == "ddos":
        data = request.json
        target_url = data.get("target_url")
        num_threads = data.get("num_threads", 500)
        duration = data.get("duration", 20)
        result_message = asyncio.run(ddos_attack(target_ip, num_threads, duration))
    elif attack_type == "htmlinjection":
        result_message = html_injection(target_ip) 
    elif attack_type == "csrf":
        result_message = csrf_vulnerability_scan(target_ip)  
    else:
        result_message = "Type d'attaque non reconnu."

    # Sérialiser les résultats si nécessaire
    if isinstance(result_message, (dict, list)):
        result_message = json.dumps(result_message)

    # Enregistrer dans la base de données
    attack_record = Attack(attack_type=attack_type, target_ip=target_ip, result=result_message)
    db.create_all()
    db.session.add(attack_record)
    db.session.commit()

    # Retourner le résultat
    results['Messages'] = result_message
    return jsonify(results)

@main.route('/attacks', methods=['GET'])
def get_attacks_pdf():
    # Récupérer toutes les attaques de la base de données
    attacks = Attack.query.all()

    # Définir le chemin pour le fichier PDF
    report_dir = os.path.join(current_app.root_path, 'static', 'reports') 
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    pdf_path = os.path.join(report_dir, 'report.pdf')

    # Générer le fichier PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)

    # Titre du rapport
    c.drawString(100, height - 50, "Attacks Report")

    # En-têtes des colonnes
    c.drawString(50, height - 80, "ID")
    c.drawString(100, height - 80, "Type d'Attaque")
    c.drawString(250, height - 80, "IP Cible")
    c.drawString(350, height - 80, "Résultat")
    c.drawString(450, height - 80, "Timestamp")

    y_position = height - 100

    # Écrire les données dans le PDF
    for attack in attacks:
        if y_position < 50:  # Nouvelle page si nécessaire
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50

        # Désérialiser le résultat si c'est du JSON
        result = attack.result
        try:
            result = json.loads(result)
        except (ValueError, TypeError):
            pass

        c.drawString(50, y_position, str(attack.id))
        c.drawString(100, y_position, attack.attack_type[:30])
        c.drawString(250, y_position, attack.target_ip[:40])
        c.drawString(350, y_position, str(result)[:30])
        c.drawString(450, y_position, attack.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        y_position -= 20  # Descendre d'une ligne

    c.save()  # Sauvegarder le PDF

    # Envoyer le fichier PDF en tant que pièce jointe
    return send_file(pdf_path, as_attachment=True)
