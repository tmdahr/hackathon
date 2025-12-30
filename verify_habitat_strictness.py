import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = 17

def test_fishing_habitat(habitat_input, expected_habitat=None):
    print(f"\n[Test] Fishing in: '{habitat_input}'")
    url = f"{BASE_URL}/game/fish?user_id={USER_ID}&habitat={habitat_input}"
    response = requests.post(url)
    
    if response.status_code == 200:
        data = response.json()
        if "fish" in data and data["fish"]:
            fish_name = data["fish"]["name"]
            fish_habitat = data["fish"]["habitat"]
            fish_type = data["fish"]["type"]
            print(f"  Caught: {fish_name} (Habitat: {fish_habitat}, Type: {fish_type})")
            
            if fish_type != 0: # Not trash
                if expected_habitat and fish_habitat != expected_habitat:
                    print(f"  [FAIL] Mismatch! Expected {expected_habitat}, but got {fish_habitat}")
                else:
                    print(f"  [PASS] Habitat matches.")
            else:
                print("  [INFO] Caught trash (Type 0). Trash is allowed if its habitat is '쓰레기'.")
        else:
            print(f"  Message: {data.get('message')}")
            if "발견되지 않음" in data.get("message"):
                print("  [PASS] Handled invalid habitat correctly.")
    else:
        print(f"  [Error] {response.status_code}: {response.text}")

if __name__ == "__main__":
    # 1. Normal habitat
    test_fishing_habitat("하구역", "하구역")
    
    # 2. Habitat with whitespace
    test_fishing_habitat("  하구역  ", "하구역")
    
    # 3. Invalid habitat
    test_fishing_habitat("화성", None)
    
    # 4. Another habitat
    test_fishing_habitat("바다", "바다")
    
    # 5. Stress test for 하구역
    print("\n[Stress Test] 20 fishing attempts in 하구역...")
    leaks = 0
    for i in range(20):
        url = f"{BASE_URL}/game/fish?user_id={USER_ID}&habitat=하구역"
        r = requests.post(url)
        d = r.json()
        if d.get("fish") and d["fish"]["type"] != 0:
            if d["fish"]["habitat"] != "하구역":
                print(f"  [LEAK] {d['fish']['name']} ({d['fish']['habitat']}) appeared in 하구역!")
                leaks += 1
    if leaks == 0:
        print("  [PASS] No leaks found in 20 attempts.")
    else:
        print(f"  [FAIL] Found {leaks} leaks.")
