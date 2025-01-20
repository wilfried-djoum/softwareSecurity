import time
import random
import requests
from threading import Thread, Lock
import asyncio
from playwright.async_api import async_playwright
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

# Initialisation des résultats
results = {
    "total_requests": 0,
    "successful_responses": 0,
    "error_responses": 0,
    "timeouts": 0,
    "errors": 0,
    "latencies": [],
}

# Lock pour synchroniser l'accès aux résultats
lock = Lock()

# Méthodes HTTP disponibles pour les tests
methods = ["GET", "POST", "HEAD"]

def send_request(url, results, method):
    """
    Envoie une requête HTTP et enregistre les résultats.
    """
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, data={'param': 'test'}, timeout=5)
        elif method == "HEAD":
            response = requests.head(url, timeout=5)

        latency = time.time() - start_time

        with lock:  # Protéger l'accès concurrent à la liste
            results["total_requests"] += 1
            if response.status_code == 200:
                results["successful_responses"] += 1
            else:
                results["error_responses"] += 1
            results["latencies"].append(latency)

        print(f"Method: {method}, Response Code: {response.status_code}, Latency: {latency:.2f}s")
    except requests.exceptions.Timeout:
        with lock:
            results["timeouts"] += 1
            results["total_requests"] += 1
        print("Request failed: Timeout")
    except requests.exceptions.RequestException as e:
        with lock:
            results["errors"] += 1
            results["total_requests"] += 1
        print(f"Request failed: {e}")

async def dos_attack(target_ip, request_count=100, interval=100, duration=10, thread_count=10):
    threads = []
    end_time = time.time() + duration

    while time.time() < end_time:
        for _ in range(thread_count):
            # Choisir une méthode HTTP aléatoire à chaque requête
            method = random.choice(methods)
            thread = Thread(target=send_request, args=(target_ip, results, method))
            threads.append(thread)
            thread.start()

        # Attendre que les threads en cours se terminent
        for thread in threads:
            thread.join()
        threads = []

    # Résultats finaux
    print("\n=== Résultats de l'attaque DoS ===")
    print(f"Requêtes réussies : {results['successful_responses']}")
    print(f"Réponses d'erreur : {results['error_responses']}")
    print(f"Timeouts : {results['timeouts']}")
    print(f"Erreurs : {results['errors']}")
    print(f"Latence moyenne : {sum(results['latencies']) / len(results['latencies']) if results['latencies'] else 0:.2f}s")

    # Détection de vulnérabilité
    if results["timeouts"] > 0 or results["error_responses"] > 0:
        return "Vulnérabilité potentielle : le serveur a échoué à répondre à certaines requêtes."
    return "Aucune vulnérabilité apparente détectée."

def generate_report(results, vulnerability_result):
    """
    Génère un rapport en PDF des résultats du test DoS avec la conclusion de vulnérabilité.
    """
    print("Génération du rapport PDF...")  # Message de débogage
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre du rapport
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="DoS Attack Test Report", ln=True, align='C')

    # Ajouter la conclusion sur la vulnérabilité
    pdf.set_font('Arial', 'I', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Conclusion: {vulnerability_result}")

    # Ajouter les résultats sous forme de texte
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Requests: {results['total_requests']}", ln=True)
    pdf.cell(200, 10, txt=f"Successful Responses: {results['successful_responses']}", ln=True)
    pdf.cell(200, 10, txt=f"Error Responses: {results['error_responses']}", ln=True)
    pdf.cell(200, 10, txt=f"Timeouts: {results['timeouts']}", ln=True)
    pdf.cell(200, 10, txt=f"Slow Responses (> 2s): {sum(1 for latency in results['latencies'] if latency > 2)}", ln=True)
    pdf.cell(200, 10, txt=f"Average Latency: {sum(results['latencies']) / len(results['latencies']) if results['latencies'] else 0:.2f}s", ln=True)

    # Ajouter un graphique de latence
    plt.figure(figsize=(6, 4))
    plt.plot(results['latencies'], label='Latency (s)')
    plt.xlabel('Request Number')
    plt.ylabel('Latency (s)')
    plt.title('Latency per Request')
    plt.savefig('latency_plot.png')  # Sauvegarde le graphique
    plt.close()

    # Vérifier si le graphique est bien généré
    if os.path.exists('latency_plot.png'):
        print("Graphique généré avec succès.")
    else:
        print("Erreur lors de la génération du graphique.")

    # Ajouter l'image du graphique dans le PDF
    pdf.ln(10)
    if os.path.exists('app/static/reports/latency_plot.png'):
        pdf.image('app/static/reports/latency_plot.png', x=10, w=180)
    else:
        print("Erreur: L'image du graphique n'a pas été générée.")

    # Sauvegarder le fichier PDF
    pdf.output("app/static/reports/dos_test_report.pdf")
    print("Report saved as dos_test_report.pdf")
    """
    Génère un rapport en PDF des résultats du test DoS avec la conclusion de vulnérabilité.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre du rapport
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="DoS Attack Test Report", ln=True, align='C')

    # Ajouter la conclusion sur la vulnérabilité
    pdf.set_font('Arial', 'I', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Conclusion: {vulnerability_result}")

    # Ajouter les résultats sous forme de texte
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Requests: {results['total_requests']}", ln=True)
    pdf.cell(200, 10, txt=f"Successful Responses: {results['successful_responses']}", ln=True)
    pdf.cell(200, 10, txt=f"Error Responses: {results['error_responses']}", ln=True)
    pdf.cell(200, 10, txt=f"Timeouts: {results['timeouts']}", ln=True)
    pdf.cell(200, 10, txt=f"Slow Responses (> 2s): {sum(1 for latency in results['latencies'] if latency > 2)}", ln=True)
    pdf.cell(200, 10, txt=f"Average Latency: {sum(results['latencies']) / len(results['latencies']) if results['latencies'] else 0:.2f}s", ln=True)

    # Ajouter un graphique de latence
    plt.figure(figsize=(6, 4))
    plt.plot(results['latencies'], label='Latency (s)')
    plt.xlabel('Request Number')
    plt.ylabel('Latency (s)')
    plt.title('Latency per Request')
    try:
        plt.savefig('app/static/reports/latency_plot.png')
        print("Graphique sauvegardé avec succès.")
    except Exception as e:
        print("Erreur lors de la sauvegarde du graphique :", e)
        plt.close()

    # Ajouter l'image du graphique dans le PDF
    pdf.ln(10)
    pdf.image('app/static/reports/latency_plot.png', x=10, w=180)

    # Sauvegarder le fichier PDF
    pdf.output("app/static/reports/dos_test_report.pdf")
    print("Report saved as dos_test_report.pdf")

    # Lancer l'attaque DoS
    # vulnerability_result = asyncio.run(dos_attack(target_ip=target_url, request_count=request_count, interval=interval, duration=duration, thread_count=thread_count))

    # Générer le rapport
    # generate_report(results, vulnerability_result)
