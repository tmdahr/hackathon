import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = 5 # Using existing user ID from previous tests

def test_collection_api():
    print(f"--- Querying Collection for User {USER_ID} ---")
    response = requests.get(f"{BASE_URL}/game/collection/{USER_ID}")
    
    if response.status_code == 200:
        collection = response.json()
        print(f"Collection count: {len(collection)}")
        
        if collection:
            # Check the first item for the new field
            item = collection[0]
            print("\n[Sample Item Keys]")
            print(item.keys())
            
            if "DstcftCn" in item:
                print(f"\n[SUCCESS] 'DstcftCn' field found!")
                print(f"Value (truncated): {item['DstcftCn'][:50]}...")
            else:
                print("\n[FAIL] 'DstcftCn' field NOT found.")
        else:
            print("Collection is empty, try fishing first.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    test_collection_api()
