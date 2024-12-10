import requests

def test_error_handling(url):
    results = {}
    try:
        # Verify and add the scheme if necessary
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Case 1: Access a non-existent page
        nonexistent_page = requests.get(url + "/thispagedoesnotexist123456", timeout=5)
        results["Nonexistent Page"] = nonexistent_page.status_code

        # Case 2: Use invalid query parameters
        invalid_params = requests.get(url, params={"invalid": "%%%"}, timeout=5)
        results["Invalid Params"] = invalid_params.status_code

        # Case 3: Send unsupported POST request
        invalid_post = requests.post(url, data={"data": "test"}, timeout=5)
        results["Invalid POST"] = invalid_post.status_code

        # Case 4: Send a request with malformed headers
        malformed_headers = requests.get(url, headers={"Malformed": "\x00"}, timeout=5)
        results["Malformed Headers"] = malformed_headers.status_code

        # Case 5: Access a URL with excessive length
        long_url = requests.get(url + "/" + "a" * 5000, timeout=5)
        results["Long URL"] = long_url.status_code

        # Case 6: Unauthorized DELETE request
        unauthorized_delete = requests.delete(url, timeout=5)
        results["Unauthorized DELETE"] = unauthorized_delete.status_code

        # Analyze the results to detect vulnerabilities
        vulnerable = any(
            status == 200
            for key, status in results.items()
            if isinstance(status, int)
        )

        if vulnerable:
            print("Vulnerable website detected: Error Handling")
        else:
            print("Not Vulnerable website: Error Handling")

    except requests.exceptions.RequestException as e:
        # Capture any exception and store it in the results
        results["Error"] = str(e)

    return results