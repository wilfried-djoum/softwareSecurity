import requests
from urllib.parse import urljoin, quote


def check_directory_traversal(url, test_paths):

    # Vérifie si le serveur est vulnérable à des attaques de type Directory Traversal.

    vulnerable_paths = []

    for path in test_paths:
        # Encoder les caractères spéciaux dans l'URL
        encoded_path = quote(path)

        # Créer l'URL complète en combinant l'URL cible et le chemin à tester
        target_url = urljoin(url, encoded_path)

        # Tenter une requête HTTP GET pour voir si le fichier est accessible
        try:
            response = requests.get(target_url)

            # Si la réponse est 200 (OK), cela pourrait indiquer une vulnérabilité
            if response.status_code == 200:
                print(f"[!] Potentiel accès réussi : {target_url}")
                vulnerable_paths.append(target_url)
            else:
                print(f"[.] Pas vulnérable (status {response.status_code}): {target_url}")

        except requests.exceptions.RequestException as e:
            print(f"[.] Erreur lors de l'accès à {target_url}: {str(e)}")

    return vulnerable_paths


def directory_traversal_report(url):

    # Fonction principale qui génère un rapport pour détecter les vulnérabilités de Directory Traversal.

    print(f"Analyzing directory traversal vulnerabilities for: {url}")

    # Liste de chemins à tester (variantes de traversée de répertoires)
    test_paths = [
        "../",  # Essayer de remonter d'un répertoire
        "../../",  # Essayer de remonter de deux répertoires
        "../../../../etc/passwd",  # Exemple d'accès à un fichier sensible (Linux)
        "../../../windows/system32/config",  # Exemple pour Windows (fichier de config système)
        "..%2F",  # URL encode du caractère '/' (percent encoding)
        "..%2F..%2F",  # Encoder la traversée à deux niveaux
        "....//....//....//etc/passwd"  # Utiliser une variation dans le nom
    ]

    # Vérifier les chemins et détecter les vulnérabilités
    vulnerable_paths = check_directory_traversal(url, test_paths)

    # Générer un rapport
    if vulnerable_paths:
        print("\n[!] Rapport de vulnérabilité Directory Traversal :")
        print(f"Serveur cible : {url}")
        print("Les chemins suivants sont vulnérables ou potentiellement vulnérables :")
        for path in vulnerable_paths:
            print(f"- {path}")
    else:
        print("\n[.] Aucune vulnérabilité Directory Traversal détectée.")

