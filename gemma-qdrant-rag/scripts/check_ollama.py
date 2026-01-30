import requests
try:
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        models = [m['name'] for m in response.json()['models']]
        print(f"Available models: {models}")
    else:
        print(f"Error {response.status_code}")
except Exception as e:
    print(f"Failed: {e}")
