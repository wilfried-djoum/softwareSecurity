import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import tkinter as tk
from tkinter import font

# Classe pour la vérification CSRF
class CSRFChecker:
    def __init__(self, driver, target_url):
        self.driver = driver
        self.target_url = target_url
        self.report = []
        self.vulnerable_forms = 0
        self.total_forms = 0

    def find_forms(self):
        """Trouve tous les formulaires de la page cible."""
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup.find_all('form')

    def check_csrf(self, form, form_index):
        """Vérifie si un formulaire est protégé contre les attaques CSRF."""
        action = form.get('action')
        method = form.get('method', 'get').lower()
        inputs = form.find_all('input')

        full_action_url = urljoin(self.target_url, action)
        csrf_protected = any('csrf' in input.get('name', '').lower() for input in inputs)

        if not csrf_protected:
            self.vulnerable_forms += 1
            self.report.append(f"Form #{form_index}:")
            self.report.append(f"  - Action URL: {full_action_url}")
            self.report.append(f"  - Method: {method.upper()}")
            self.report.append(f"  - Inputs: {', '.join(input.get('name', 'N/A') for input in inputs)}")
            self.report.append(f"  [!] Status: Vulnerable to CSRF attacks")
        else:
            self.report.append(f"Form #{form_index}:")
            self.report.append(f"  - Action URL: {full_action_url}")
            self.report.append(f"  - Method: {method.upper()}")
            self.report.append(f"  - Inputs: {', '.join(input.get('name', 'N/A') for input in inputs)}")
            self.report.append(f"  [+] Status: CSRF protection detected")

    def run(self):
        """Exécute la vérification CSRF sur les formulaires de l'URL cible."""
        self.report = [
            f"CSRF Vulnerability Scan Report\n{'=' * 50}",
            f"Target URL: {self.target_url}",
            f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
        ]

        forms = self.find_forms()
        self.total_forms = len(forms)

        if not forms:
            self.report.append("No forms found on the target page.")
        else:
            self.report.append(f"Number of forms found: {self.total_forms}\n")
            # Tester uniquement le premier formulaire
            self.check_csrf(forms[0], 1)

        self.report.append("\n" + "=" * 50)
        self.report.append("Summary of Results\n" + "=" * 50)
        self.report.append(f"Total forms analyzed: {self.total_forms}")
        self.report.append(f"Vulnerable forms detected: {self.vulnerable_forms}")
        self.report.append(f"Forms with CSRF protection: {self.total_forms - self.vulnerable_forms}")

        self.report.append("\n" + "=" * 50)
        self.report.append("Recommendations\n" + "=" * 50)
        if self.vulnerable_forms > 0:
            self.report.append("1. Implement CSRF tokens for all forms to prevent unauthorized requests.")
            self.report.append("2. Ensure CSRF tokens are unique, unpredictable, and tied to user sessions.")
            self.report.append("3. Validate CSRF tokens server-side for every request.")
        else:
            self.report.append("All forms are CSRF-protected. No action required.")

        return "\n".join(self.report)


# Fonction de login avec Selenium
def login(driver, login_url, username, password):
    """Se connecter à la page de login."""
    driver.get(login_url)
    print(f"Navigating to login page: {login_url}")

    # Trouver les champs de login
    username_field = driver.find_element(By.NAME, "login")
    password_field = driver.find_element(By.NAME, "password")

    # Remplir les champs et soumettre le formulaire
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    print("Logging in...")
    time.sleep(3)  # Attendre que la page se charge


# Test CSRF avec login
def run_csrf_with_login(login_url, target_url, username, password):
    """Tester la vulnérabilité CSRF après connexion."""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = []

    try:
        # Étape 1 : Login
        login(driver, login_url, username, password)

        # Étape 2 : Naviguer vers l'URL cible après le login
        print(f"Navigating to target URL: {target_url}")
        driver.get(target_url)
        time.sleep(7)


        # Étape 3 : Tester les vulnérabilités CSRF sur l'URL cible
        checker = CSRFChecker(driver, target_url)
        report = checker.run()

    except Exception as e:
        report.append(f"Error during CSRF test: {e}")
    finally:
        driver.quit()

    return report

def test_html_injection_with_login_once(login_url, target_url, username, password, payload):

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = []

    try:
        # Étape 1 : Login
        driver.get(login_url)
        print(f"Navigating to login page: {login_url}")
        
        # Trouver et remplir les champs de login
        driver.find_element(By.NAME, "login").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        print("Logged in.")
        time.sleep(3)  # Attendre que la connexion soit effectuée

        # Étape 2 : Tester l'injection HTML
        driver.get(target_url)
        report.append(f"Testing HTML Injection on URL: {target_url}")

        # Charger la page cible et analyser les formulaires
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        forms = soup.find_all('form')

        if not forms:
            report.append("No forms found on the page.")
        else:
            report.append(f"Number of forms found: {len(forms)}")

        # Traiter le premier formulaire trouvé
        form = forms[0] if forms else None
        if form:
            report.append("Testing Form #1")
            inputs = form.find_all(['input', 'textarea'])

            # Remplir les champs de formulaire
            for input_field in inputs:
                input_name = input_field.get('name')
                if input_name:
                    input_element = driver.find_element(By.NAME, input_name)
                    input_element.clear()
                    input_element.send_keys(payload)

            # Soumettre le formulaire
            try:
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                ActionChains(driver).move_to_element(submit_button).click().perform()
            except Exception:
                try:
                    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    submit_button.click()
                except Exception as e:
                    report.append(f"Error submitting the form: {e}")
                    return "\n".join(report)

            time.sleep(3)

            # Vérifier si le payload est reflété dans la page
            if payload in driver.page_source:
                report.append(f"🚨 Form #1 is vulnerable to HTML Injection!")
            else:
                report.append(f"✅ Form #1 appears safe from HTML Injection.")
        else:
            report.append("No form available to test.")

    except Exception as e:
        report.append(f"Error during test: {e}")
    finally:
        driver.quit()

    return "\n".join(report)

# Interface graphique (GUI)
def start_attack():
    attack_type = attack_var.get()
    login_url = "http://localhost:81/bwapp-master/bWAPP/login.php"
    username = "bee"
    password = "bug"

    target_url = url_entry.get()
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url

    if attack_type == "CSRF":
        report = run_csrf_with_login(login_url, target_url, username, password)
    elif attack_type == "HTML Injection":
        payload = "<h1>Injected Content</h1>"
        report = test_html_injection_with_login_once(login_url, target_url, username, password, payload)
    else:
        report = "Invalid attack type."

    report_text.delete(1.0, tk.END)
    report_text.insert(tk.END, report)


# Configuration de l'interface GUI
root = tk.Tk()
root.title("Security Testing Tool")
root.geometry("800x600")
root.configure(bg="#2e3d49")

# Police personnalisée
title_font = font.Font(family="Arial", size=14, weight="bold")
label_font = font.Font(family="Arial", size=12)
text_font = font.Font(family="Courier", size=10)

frame = tk.Frame(root, padx=10, pady=10, bg="#2e3d49")
frame.pack(fill="x")

attack_var = tk.StringVar(value="CSRF")

csrf_button = tk.Radiobutton(frame, text="CSRF Attack", variable=attack_var, value="CSRF", bg="#2e3d49", fg="white", font=label_font, selectcolor="#3b4e61")
csrf_button.pack(side="left", padx=10)

html_injection_button = tk.Radiobutton(frame, text="HTML Injection", variable=attack_var, value="HTML Injection", bg="#2e3d49", fg="white", font=label_font, selectcolor="#3b4e61")
html_injection_button.pack(side="left", padx=10)

url_label = tk.Label(frame, text="Target URL:", bg="#2e3d49", fg="white", font=label_font)
url_label.pack(side="left", padx=5)

url_entry = tk.Entry(frame, width=50, font=text_font)
url_entry.pack(side="left", fill="x", expand=True, padx=5)

run_button = tk.Button(frame, text="Run Test", command=start_attack, bg="#4CAF50", fg="white", font=label_font, relief="flat", width=12)
run_button.pack(side="right", padx=5)

report_frame = tk.Frame(root, padx=10, pady=10, bg="#2e3d49")
report_frame.pack(fill="both", expand=True)

report_label = tk.Label(report_frame, text="Report:", bg="#2e3d49", fg="white", font=label_font)
report_label.pack(anchor="w")

report_text = tk.Text(report_frame, wrap="word", height=20, font=text_font, bg="#1e2a33", fg="white", insertbackground="white", relief="flat")
report_text.pack(fill="both", expand=True)

root.mainloop()
