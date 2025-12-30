import requests
import json
import time

BASE_URL = "http://localhost:8000"

def create_user(nickname):
    response = requests.post(f"{BASE_URL}/users", json={"nickname": nickname})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400: # Already exists
        # Try to guess ID or specific query if implemented, but here we just fallback
        pass
    return None

def test_fishing(user_id, habitat, description):
    print(f"\n--- {description} (Habitat: {habitat}) ---")
    response = requests.post(f"{BASE_URL}/game/fish", params={"user_id": user_id, "habitat": habitat})
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('fish'):
        fish = data['fish']
        print(f"Caught: {fish['name']} (Type: {fish['type']})")
        print(f"Response Habitat in Fish: {fish.get('habitat', 'MISSING')}")
        
        # Verify trash logic
        if fish['type'] == 0:
            print("[CHECK] Caught TRASH. This should be possible regardless of habitat.")
        else:
            print(f"[CHECK] Caught Normal/Other. Should match habitat '{habitat}'. Fish Habitat: '{fish.get('habitat')}'")
            if fish.get('habitat') != habitat:
                print("!!! WARNING: Habitat mismatch for non-trash species !!!")
    else:
        print(f"Response Message: {data.get('message')}")

def main():
    # 1. Setup User (Reuse or Create)
    # Using ID 5 from previous run if possible, or create new
    user_id = 5 
    print(f"Using User ID: {user_id}")

    # 2. Test Normal Catch (Valid Habitat)
    test_fishing(user_id, "갯벌", "Testing Valid Habitat")

    # 3. Test Trash Logic (Loop until trash is caught or max tries)
    # We need to simulate a very dirty user to increase trash probability
    # OR since we can't easily set pollution without DB access or fishing trash, 
    # we just try many times in a weird habitat.
    # If we fish in "Space" (Invalid Habitat), ONLY trash should be possible (if pollution allows) 
    # OR nothing if current probability logic weights trash as 0.
    
    # Actually, if pollution is low, trash weight might be low.
    # But let's try an invalid habitat. If non-trash, it should return nothing.
    # If trash, it returns trash.
    print("\n--- Testing Trash in Invalid Habitat (Space) ---")
    caught_trash = False
    for i in range(10):
        response = requests.post(f"{BASE_URL}/game/fish", params={"user_id": user_id, "habitat": "우주"})
        data = response.json()
        if data.get('fish') and data['fish']['type'] == 0:
            print(f"Iter {i+1}: SUCCESSS! Caught Trash in Space: {data['fish']['name']}")
            print(f"Habitat in response: {data['fish'].get('habitat')}")
            caught_trash = True
            break
        elif data.get('fish'):
            print(f"Iter {i+1}: FAIL? Caught non-trash in Space? {data['fish']['name']} ({data['fish']['type']})")
        else:
            # Nothing caught, which is expected if we didn't roll trash
            # print(f"Iter {i+1}: Nothing caught.")
            pass
            
    if not caught_trash:
        print("Did not catch trash in 10 tries (maybe luck or low pollution).")

if __name__ == "__main__":
    main()
