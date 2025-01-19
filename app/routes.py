import asyncio
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import Attack
from app import db
import time
import os
from app.attacks import brute_force_attack
from app.attacks import sql_injection_attack
from app.attacks import error_handling_attack
from app.attacks import vulnerable_library_attack
from app.attacks import dos_attack
from app.attacks import xss_attack
from app.attacks import xxe_attack

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')


@main.route('/attack', methods = ['POST'])
def attack():
    attack_type = request.json['attackType']
    target_ip = request.json['targetIP']
    results = {}
    
    # simulation du temps d'exécution d'une attaque a 3secondes
    time.sleep(3)
    
    # implementation de la logique des attaques 
    if attack_type == "bruteForce":
       result_message = brute_force_attack(target_ip)
    elif attack_type == "sqlInjection":
        result_message = asyncio.run(sql_injection_attack(target_ip))
    elif attack_type == "xss":
        result_message = asyncio.run(xss_attack(target_ip))
    elif attack_type == "xxe":
        result_message = asyncio.run(xxe_attack(target_ip))
    elif attack_type == "vulnerableLibrary":
        result_message = asyncio.run(vulnerable_library_attack(target_ip))
    elif attack_type == "errorhandling":
        result_message = asyncio.run(error_handling_attack(target_ip))
    elif attack_type == "dos_attack":
        result_message = asyncio.run(dos_attack(target_ip))
    else:
        result_message = "Type d'attaque non reconnu."
    
    # enregistrement dans la base de données 
    attack_record = Attack(attack_type=attack_type, target_ip=target_ip, result=result_message)
    db.create_all()
    db.session.add(attack_record)
    db.session.commit()
    
    results['Messages'] = result_message
    return jsonify(results)

@main.route('/attacks', methods=['GET'])
def get_attacks_pdf():
    attacks = Attack.query.all()
    
    # Chemin du fichier PDF
    report_dir = os.path.join(current_app.root_path, 'static', 'reports') 
    # report_dir = 'static/reports'
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    pdf_path = os.path.join(report_dir, 'report.pdf')

    # Génération du fichier PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    
    # Titre du rapport
    c.drawString(100, height - 50, "Attacks Report")
    
    # En-tête des colonnes
    c.drawString(50, height - 80, "ID")
    c.drawString(100, height - 80, "Type d'Attaque")
    c.drawString(250, height - 80, "IP Cible")
    c.drawString(350, height - 80, "Résultat")
    c.drawString(450, height - 80, "Timestamp")

    y_position = height - 100
    
    # Parcourir et écrire les attaques dans le PDF
    for attact in attacks:
        if y_position < 50:  # Si on arrive au bas de la page, ajouter une nouvelle page
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50
        
        c.drawString(50, y_position, str(attact.id))
        c.drawString(100, y_position,attact.attack_type[:30])
        c.drawString(250, y_position,attact.target_ip[:40])
        c.drawString(350, y_position,attact.result[:30])
        c.drawString(450, y_position, attact.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        y_position -= 20  # Descendre d'une ligne

    c.save()  # Sauvegarder le PDF

    # Envoyer le fichier PDF en tant que pièce jointe
    return send_file(pdf_path, as_attachment=True)