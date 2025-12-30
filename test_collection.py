import requests
import json

def test_collection_api():
    url = "http://127.0.0.1:8000/game/collection/1"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Received {len(data)} items.")
            if len(data) > 0:
                print("First item sample:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_collection_api()
