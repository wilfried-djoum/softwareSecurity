import requests
from bs4 import BeautifulSoup

# Retire.js vulnerability database URL
RETIRE_JS_DB = "https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository.json"

async def vulnerable_library_attack(site_url):

    # Fetch the Retire.js vulnerability database
    def fetch_vulnerability_db():
        response = requests.get(RETIRE_JS_DB)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch the Retire.js vulnerability database.")
            return {}

    # Extract JavaScript libraries from a given web page
    def extract_js_libraries(url):
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to access the URL: {url}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        js_files = [script['src'] for script in soup.find_all("script", src=True)]
        print("Libraries:", js_files)
        return js_files

    # Compare the extracted JavaScript files with the vulnerability database
    def check_vulnerabilities(js_files, vuln_db):
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

    print("Analyzing site:", site_url)

    # Fetch JavaScript files from the target website
    js_files = extract_js_libraries(site_url)
    if not js_files:
        print("No JavaScript files found.")
        return {"status": "No JavaScript files found."}

    print("Detected JavaScript files:", js_files)

    # Fetch the vulnerability database
    vuln_db = fetch_vulnerability_db()
    if not vuln_db:
        return {"status": "Failed to fetch the vulnerability database."}

    # Check for vulnerabilities in the extracted JavaScript files
    vulnerabilities = check_vulnerabilities(js_files, vuln_db)
    if vulnerabilities:
        print("\nVulnerabilities detected:")
        for vuln in vulnerabilities:
            print(f"- Library: {vuln['library']}")
            print(f"  File: {vuln['file']}")
            print(f"  Vulnerabilities: {vuln['vulnerabilities']}")
        return {"status": "Vulnerabilities detected.", "details": "Check the list of vulnerable libraries in the terminal"}
    else:
        print("\nNo vulnerabilities detected.")
        return {"status": "No vulnerabilities detected."}
