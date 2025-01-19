import asyncio
from flask import Blueprint, request, jsonify, render_template, send_file, current_app, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import Attack
from app import db
import time
import os
from app.attacks import brute_force_attack, sql_injection_attack, rce_attack_function, phishing_attack
import textwrap
from flask import Flask
import requests

main = Blueprint('main', __name__)
app = Flask(__name__, template_folder='templates')

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/attack', methods=['POST'])
def attack():
    attack_type = request.json['attackType']
    target_ip = request.json['targetIP']
    results = {}

    time.sleep(3)  
    if attack_type == "bruteForce":
        result_message = brute_force_attack(target_ip)
    elif attack_type == "dos":
        result_message = f"DoS attack on {target_ip} executed."
    elif attack_type == "sqlInjection":
        result_message = asyncio.run(sql_injection_attack(target_ip))
    elif attack_type == "xss":
        result_message = f"Cross-Site Scripting attack on {target_ip} simulated."
    elif attack_type == "rce":
        result_message = rce_attack_function(target_ip)
    elif attack_type == "phishing":
        malicious_url = f"{target_ip}/?redirect=http://127.0.0.1:5000/phishing/fake_register"
    
        try:
            if not target_ip.startswith("http://") and not target_ip.startswith("https://"):
                target_ip = "http://" + target_ip 
            
            response = requests.get(malicious_url, headers={'Host': target_ip.split('://')[1]})
            if response.url == "http://127.0.0.1:5000/phishing/fake_register":
                result_message = f"Vulnerability detected! The site {target_ip} is vulnerable to phishing."
            else:
                result_message = f"The site {target_ip} does not appear to be vulnerable to phishing via open redirect."
        except requests.exceptions.RequestException as e:
            result_message = f"Error while testing {target_ip}: {str(e)}"

        results['message'] = result_message
        results['malicious_url'] = malicious_url
        return jsonify(results)


    else:
        result_message = "Unknown attack type."
        return jsonify({'error': result_message}), 400


    attack_record = Attack(attack_type=attack_type, target_ip=target_ip, result=result_message)
    db.create_all()
    db.session.add(attack_record)
    db.session.commit()

    results['Messages'] = result_message
    return jsonify(results)

@main.route('/redirect-handler')
def redirect_handler():
    next_url = request.args.get('next', '/')
    return redirect(next_url)

@main.route('/phishing/fake_register')
def fake_register():
    # Get the malicious redirection URL from the query parameter
    payload_url = request.args.get('redirect')
    return render_template('fake_register.html', payload_url=payload_url)

@main.route('/attacks', methods=['GET'])
def get_attacks_pdf():
    attacks = Attack.query.all()
    
    report_dir = os.path.join(current_app.root_path, 'static', 'reports') 
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    pdf_path = os.path.join(report_dir, 'report.pdf')
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

    for attact in attacks:
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50
        
        c.drawString(50, y_position, str(attact.id))
        c.drawString(100, y_position, textwrap.shorten(attact.attack_type, width=30, placeholder="..."))
        c.drawString(250, y_position, textwrap.shorten(attact.target_ip, width=40, placeholder="..."))
        c.drawString(350, y_position, textwrap.shorten(attact.result, width=30, placeholder="..."))
        c.drawString(450, y_position, attact.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        y_position -= 20

    c.save()
    return send_file(pdf_path, as_attachment=True)
