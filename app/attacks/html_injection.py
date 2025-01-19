from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

def html_injection(target_url):
    # Définir le payload directement dans le code
    payload = "<h1>Injected Content</h1>"

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    report = []

    try:
        # Étape 1 : Charger la page cible
        driver.get(target_url)
        report.append(f"Testing HTML Injection on URL: {target_url}")

        # Charger la page et analyser les formulaires
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        forms = soup.find_all('form')

        if not forms:
            report.append("No forms found on the page.")
        else:
            report.append(f"Number of forms found: {len(forms)}")

        # Tester le premier formulaire
        if forms:
            inputs = forms[0].find_all(['input', 'textarea'])

            for input_field in inputs:
                input_name = input_field.get('name')
                if input_name:
                    driver.find_element(By.NAME, input_name).send_keys(payload)

            # Soumettre le formulaire
            try:
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
            except Exception as e:
                report.append(f"Error submitting the form: {e}")

            time.sleep(3)

            # Vérifier si le payload est reflété dans la page
            if payload in driver.page_source:
                report.append("\ud83d\udea8 HTML Injection detected!")
            else:
                report.append("\u2705 No HTML Injection detected.")
    except Exception as e:
        report.append(f"Error during test: {e}")
    finally:
        driver.quit()

    return "\n".join(report)


