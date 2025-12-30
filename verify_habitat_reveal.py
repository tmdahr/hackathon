import requests

BASE_URL = "http://localhost:8000"
USER_ID = 5

def verify_uncaught_habitat():
    response = requests.get(f"{BASE_URL}/game/collection/{USER_ID}")
    data = response.json()
    
    uncaught_items = [item for item in data if not item['is_caught']]
    
    if not uncaught_items:
        print("User has caught everything! Cannot verify.")
        return

    print(f"Found {len(uncaught_items)} uncaught items.")
    sample = uncaught_items[0]
    print(f"Sample Uncaught Item: Name={sample['name']}, Habitat={sample['habitat']}")
    
    if sample['habitat'] != "???":
        print("SUCCESS: Habitat is revealed!")
    else:
        print("FAIL: Habitat is still hidden.")

if __name__ == "__main__":
    verify_uncaught_habitat()
