import requests
import json

def test_fishing_api():
    url = "http://127.0.0.1:8000/game/fish"
    params = {"user_id": 1} # Assuming user 1 exists
    
    try:
        response = requests.post(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_fishing_api()
