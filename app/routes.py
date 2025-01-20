import asyncio
import json
import os
import time
import logging
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import Attack
from app import db
import textwrap
import requests
from app.attacks import sql_injection_attack, error_handling_attack, vulnerable_library_attack, xss_attack, xxe_attack, rce_attack_function, phishing_attack
from app.attacks import ddos_attack
from app.attacks.csrf import csrf_vulnerability_scan
from app.attacks.html_injection import html_injection
from app.attacks import dos
from app.attacks import dbSchema

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    logger.info("Accès à la page d'accueil.")
    return render_template('index.html')

@main.route('/attack', methods=['POST'])
def attack():
    # Récupérer les données de la requête
    logger.info("Requête reçue pour l'attaque.")
    attack_type = request.json.get('attackType', '')
    target_ip = request.json.get('targetIP', '')
    results = {}

    logger.info(f"Type d'attaque : {attack_type}, IP cible : {target_ip}")
    
    # Simulation du temps d'exécution d'une attaque à 3 secondes
    time.sleep(3)
    
    # Implémentation de la logique des attaques 
    try:
        if attack_type == "bruteForce":
            logger.info("Démarrage de l'attaque brute force.")
            result_message = brute_force_attack(target_ip)

        elif attack_type == "dos":
            logger.info("Démarrage de l'attaque DoS.")
            request_count = 100
            interval = 100
            duration = 10
            thread_count = 10
            result_message = asyncio.run(dos.dos_attack(target_ip, request_count=request_count, interval=interval, duration=duration, thread_count=thread_count))
            dos.generate_report(dos.results, result_message)

        elif attack_type == "sqlInjection":
            logger.info("Démarrage de l'attaque SQL Injection.")
            result_message = asyncio.run(sql_injection_attack(target_ip))

        elif attack_type == "xss":
            logger.info("Simulation d'une attaque XSS.")
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
        elif attack_type == "rce":
            result_message = rce_attack_function(target_ip)
        elif attack_type == "phishing":
            malicious_url = f"{target_ip}/?redirect=http://127.0.0.1:5000/phishing/fake_register"
    
            try:
                if not target_ip.startswith("http://") and not target_ip.startswith("https://"):
                    target_ip = "http://" + target_ip 
                
                response = requests.get(malicious_url, headers={'Host': target_ip.split('://')[1]})
                if response.url == "http://127.0.0.1:5000/phishing/fake_register":
                    result_message = f"Vulnerability detected! The site {target_ip} is vulnerable to phishing.";
                else:
                    result_message = f"The site {target_ip} does not appear to be vulnerable to phishing via open redirect."
            except requests.exceptions.RequestException as e:
                result_message = f"Error while testing {target_ip}: {str(e)}"
        elif attack_type == 'dbSchema':
            logger.info("Démarrage de l'attaque de mapping de la base de données.")
            param_list = [
                "id", "name", "user", "product", "category", "action", "page", "search", "query", "filter",
                "category_id", "item", "session", "order", "price", "email", "username", "password", "key", "sort"
            ]
            result_message = dbSchema.test_parameters(f"{target_ip}", param_list)
            report_dir = os.path.join(current_app.root_path, 'static', 'reports')
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            pdf_path = os.path.join(report_dir, 'dbschema_test_report.pdf')
            dbSchema.generate_dbschema_report(result_message, pdf_path)
            logger.info(f"Rapport PDF dbSchema disponible à : {pdf_path}")
        else:
            logger.warning(f"Type d'attaque non reconnu : {attack_type}")
            result_message = "Type d'attaque non reconnu."

        # Enregistrement dans la base de données 
        logger.info("Enregistrement de l'attaque dans la base de données.")
        attack_record = Attack(attack_type=attack_type, target_ip=target_ip, result=result_message)
        db.create_all()
        db.session.add(attack_record)
        db.session.commit()
        
        results['Messages'] = result_message
        logger.info("Attaque terminée avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'attaque : {e}")
        results['Messages'] = f"Erreur : {e}"

    return jsonify(results)


@main.route('/attacks', methods=['GET'])
def get_attacks_pdf():
    logger.info("Génération du fichier PDF des attaques.")
    # Récupérer toutes les attaques de la base de données
    attacks = Attack.query.all()
    
    # Chemin du fichier PDF
    report_dir = os.path.join(current_app.root_path, 'static', 'reports') 
    # report_dir = 'static/reports'
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    pdf_path = os.path.join(report_dir, 'report.pdf')

    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 50, "Attacks Report")
        c.drawString(50, height - 80, "ID")
        c.drawString(100, height - 80, "Type d'Attaque")
        c.drawString(250, height - 80, "IP Cible")
        c.drawString(350, height - 80, "Résultat")
        c.drawString(450, height - 80, "Timestamp")

        y_position = height - 100

        for attack in attacks:
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50
            
            c.drawString(50, y_position, str(attack.id))
            c.drawString(100, y_position, attack.attack_type[:30])
            c.drawString(250, y_position, attack.target_ip[:40])
            c.drawString(350, y_position, attack.result[:30])
            c.drawString(450, y_position, attack.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            y_position -= 20

        c.save()
        logger.info("Fichier PDF généré avec succès.")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du fichier PDF : {e}")
        return jsonify({"error": str(e)}), 500
