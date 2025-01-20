import socket
import dns.resolver

def generate_typosquatting_variants(domain):
    # Génère une liste de variantes typographiques (typosquatting) d'un domaine populaire.

    base = domain.split('.')[0]
    typos = set()

    # Remplacer des lettres similaires
    typo_replacements = {
        'a': ['@', '4'],
        'e': ['3'],
        'o': ['0'],
        'i': ['1', 'l'],
        's': ['5'],
        'g': ['9'],
    }

    # Modifier les lettres dans le domaine
    for letter, replacements in typo_replacements.items():
        for rep in replacements:
            typos.add(base.replace(letter, rep))

    # Ajouter des fautes de frappe courantes (lettres voisines sur le clavier)
    keyboard_neighbors = {
        'q': ['w', 'a'],
        'w': ['q', 'e', 's'],
        'e': ['w', 'r', 'd'],
        'r': ['e', 't', 'f'],
        't': ['r', 'y', 'g'],
        'y': ['t', 'u', 'h'],
        'u': ['y', 'i', 'j'],
        'i': ['u', 'o', 'k'],
        'o': ['i', 'p', 'l'],
        'p': ['o', ';'],
        # ... (ajouter d'autres lettres si nécessaire)
    }

    # Créer toutes les permutations possibles en remplaçant une lettre par ses voisines sur le clavier
    for letter, neighbors in keyboard_neighbors.items():
        for variant in neighbors:
            typos.add(base.replace(letter, variant))

    return list(typos)


def check_if_domain_exists(domain):
    # Vérifie si un domaine existe en effectuant une requête DNS.

    try:
        result = dns.resolver.resolve(domain, 'A')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False


def typosquatting_report(ip_address):
    # Fonction principale qui analyse les typosquatting pour un domaine donné par son adresse IP.

    try:
        # Résolution du nom de domaine à partir de l'adresse IP
        domain = socket.gethostbyaddr(ip_address)[0]
        print(f"Domaine cible: {domain}")
    except (socket.herror, socket.gaierror):
        print(f"Erreur de résolution pour l'IP {ip_address}")
        return

    # Générer des variantes de typosquatting pour le domaine
    typos = generate_typosquatting_variants(domain)

    # Vérifier chaque domaine généré pour savoir s'il existe
    existing_domains = []
    for typo in typos:
        if check_if_domain_exists(typo + ".com"):
            existing_domains.append(typo + ".com")

    # Générer le rapport
    if existing_domains:
        print("\nRapport de Typosquatting :")
        print(f"Domaine cible : {domain}")
        print(f"Les variantes de domaines similaires trouvées :")
        for ed in existing_domains:
            print(f"- {ed}")
    else:
        print(f"Aucune variante de typosquatting trouvée pour {domain}.")
