from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

def csrf_vulnerability_scan(target_url):
    """Teste la vulnérabilité CSRF sur une URL cible après connexion."""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = []
    vulnerable_forms = 0
    total_forms = 0

    try:
        # Étape 2 : Charger l'URL cible
        driver.get(target_url)
        time.sleep(3)

        # Étape 3 : Analyser les formulaires
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        forms = soup.find_all('form')
        total_forms = len(forms)

        report.append(f"CSRF Vulnerability Scan Report\n{'=' * 50}")
        report.append(f"Target URL: {target_url}")
        report.append(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)

        if not forms:
            report.append("No forms found on the target page.")
        else:
            report.append(f"Number of forms found: {total_forms}\n")

            # Vérifier chaque formulaire
            for i, form in enumerate(forms, start=1):
                action = form.get('action', 'N/A')
                method = form.get('method', 'GET').upper()
                inputs = form.find_all('input')

                full_action_url = urljoin(target_url, action)
                csrf_protected = any('csrf' in input.get('name', '').lower() for input in inputs)

                report.append(f"Form #{i}:")
                report.append(f"  - Action URL: {full_action_url}")
                report.append(f"  - Method: {method}")
                report.append(f"  - Inputs: {', '.join(input.get('name', 'N/A') for input in inputs)}")

                if not csrf_protected:
                    vulnerable_forms += 1
                    report.append(f"  [!] Status: Vulnerable to CSRF attacks")
                else:
                    report.append(f"  [+] Status: CSRF protection detected")

        # Résumé des résultats
        report.append("\n" + "=" * 50)
        report.append("Summary of Results\n" + "=" * 50)
        report.append(f"Total forms analyzed: {total_forms}")
        report.append(f"Vulnerable forms detected: {vulnerable_forms}")
        report.append(f"Forms with CSRF protection: {total_forms - vulnerable_forms}")

        # Recommandations
        report.append("\n" + "=" * 50)
        report.append("Recommendations\n" + "=" * 50)
        if vulnerable_forms > 0:
            report.append("1. Implement CSRF tokens for all forms to prevent unauthorized requests.")
            report.append("2. Ensure CSRF tokens are unique, unpredictable, and tied to user sessions.")
            report.append("3. Validate CSRF tokens server-side for every request.")
        else:
            report.append("All forms are CSRF-protected. No action required.")

    except Exception as e:
        report.append(f"Error during CSRF test: {e}")
    finally:
        driver.quit()

    return "\n".join(report)



