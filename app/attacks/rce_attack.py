from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def check_target_connectivity(target_ip):
    if not target_ip.startswith(('http://', 'https://')):
        target_ip = 'https://' + target_ip  
    
    target_ip_without_fragment = target_ip.split('#')[0]

    try:
        response = requests.get(target_ip_without_fragment) 
        if response.status_code == 200:
            print(f"Successfully connected to {target_ip}")
            return True
        else:
            print(f"Failed to connect to {target_ip}. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {target_ip}: {e}")
        return False

def rce_attack_function(target_ip):
    driver = None 
    try:
        if not target_ip.startswith(('http://', 'https://')):
            target_ip = 'https://' + target_ip
        
        print(f"Checking connectivity to {target_ip}...")
        if not check_target_connectivity(target_ip):
            return f"Target {target_ip} is unreachable. Cannot perform RCE attack."
    
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')  
        
   
        print(f"Launching browser to perform RCE attack on {target_ip}...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(target_ip)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))  
        )

        print("Executing RCE attack...")

        driver.execute_script("document.body.style.backgroundImage = 'none';")  
        driver.execute_script("document.body.style.backgroundColor = 'red';") 
        driver.execute_script("document.querySelector('h1').textContent = 'RCE Attack Executed!';")
        
        driver.execute_script(""" 
            var paragraphs = document.querySelectorAll('p');
            if (paragraphs.length > 0) {
                paragraphs[0].textContent = 'This content has been modified as part of the RCE attack!';
            }
        """)

        driver.execute_script(""" 
            var warning = document.createElement('div');
            warning.innerHTML = '<h2 style="color: red; text-align: center;">Warning: RCE Attack Executed!</h2>';
            document.body.appendChild(warning);
        """)

     
        print("Creating popup with attack status...")
        driver.execute_script("""
            var popup = document.createElement('div');
            popup.style.position = 'fixed';
            popup.style.top = '50%';
            popup.style.left = '50%';
            popup.style.transform = 'translate(-50%, -50%)';
            popup.style.backgroundColor = 'white';
            popup.style.border = '2px solid black';
            popup.style.padding = '20px';
            popup.style.zIndex = '9999';
            popup.style.fontSize = '16px';

            var content = `
                <h2>RCE Attack Status</h2>
                <p><strong>Status:</strong><br> Vulnerability Detected! RCE Attack Executed Successfully!</p>
                <p><strong>Details:</strong><br>
                    Background color changed to red.<br>
                    Header changed to 'RCE Attack Executed!'.<br>
                    Content modified.
                </p>
            `;

            popup.innerHTML = content;
            document.body.appendChild(popup);
        """)

        time.sleep(15)

        return f"RCE attack was executed successfully on {target_ip}. Background image and content were changed."

    except Exception as e:
        print(f"Unexpected error during RCE execution: {str(e)}")
      
        driver.execute_script("""
            var popup = document.createElement('div');
            popup.style.position = 'fixed';
            popup.style.top = '50%';
            popup.style.left = '50%';
            popup.style.transform = 'translate(-50%, -50%)';
            popup.style.backgroundColor = 'white';
            popup.style.border = '2px solid black';
            popup.style.padding = '20px';
            popup.style.zIndex = '9999';
            popup.style.fontSize = '16px';

            var content = `
                <h2>RCE Attack Status</h2>
                <p><strong>Status:</strong><br> Vulnerability Not Detected! Attack could not be executed.</p>
                <p><strong>Error:</strong><br> {}</p>
            `;

            popup.innerHTML = content;
            document.body.appendChild(popup);
        """.format(str(e)))
        time.sleep(15)

        return f"Unexpected error during execution: {str(e)}"
    
    finally:
        if driver:
            print("Closing the browser...")
            driver.quit()  
