import requests
from bs4 import BeautifulSoup

# Retire.js vulnerability database URL
RETIRE_JS_DB = "https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository.json"

def fetch_vulnerability_db():
    """Fetch the Retire.js vulnerability database."""
    response = requests.get(RETIRE_JS_DB)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch the Retire.js vulnerability database.")
        return {}

def extract_js_libraries(url):
    """Extract JavaScript libraries from a web page."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to access the URL: {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    js_files = []
    for script in soup.find_all("script", src=True):
        js_files.append(script['src'])

    print("Libraries:", js_files)
    return js_files

def check_vulnerabilities(js_files, vuln_db):
    """Compare JavaScript files with the vulnerability database."""
    vulnerable_libraries = []
    for js_file in js_files:
        for lib_name, data in vuln_db.items():
            if lib_name in js_file:
                vulnerable_libraries.append({
                    "library": lib_name,
                    "file": js_file,
                    "vulnerabilities": data.get("vulnerabilities", [])
                })
    return vulnerable_libraries

def main():
    # URL of the website to analyze
    site_url = "https://www.isep.fr/"

    print("Analyzing site:", site_url)
    # Fetch JavaScript files
    js_files = extract_js_libraries(site_url)
    if not js_files:
        print("No JavaScript files found.")
        return

    print("Detected JavaScript files:", js_files)
    # Fetch the vulnerability database
    vuln_db = fetch_vulnerability_db()
    if not vuln_db:
        return

    # Check for vulnerabilities
    vulnerabilities = check_vulnerabilities(js_files, vuln_db)
    if vulnerabilities:
        print("\nVulnerabilities detected:")
        for vuln in vulnerabilities:
            print(f"- Library: {vuln['library']}")
            print(f"  File: {vuln['file']}")
            print(f"  Vulnerabilities: {vuln['vulnerabilities']}")
    else:
        print("\nNo vulnerabilities detected.")

if __name__ == "__main__":
    main()
