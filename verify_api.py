import requests
import json

BASE_URL = "http://localhost:8000"

def create_user(nickname):
    response = requests.post(f"{BASE_URL}/users", json={"nickname": nickname})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400: # Already exists
        # Try login/get info (assuming we can just use the ID if we knew it, but for now let's assume valid ID 1 if fails)
        # Actually, let's just ignore and assume ID 1 exists if we can't create.
        pass
    return None

def test_fishing(user_id, habitat):
    print(f"Fishing in {habitat}...")
    response = requests.post(f"{BASE_URL}/game/fish", params={"user_id": user_id, "habitat": habitat})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    # 1. Create User
    nickname = "test_fisher"
    user = create_user(nickname)
    if user:
        user_id = user['id']
        print(f"Created user with ID: {user_id}")
    else:
        # Fallback to ID 1
        user_id = 1
        print(f"Using fallback User ID: {user_id}")

    # 2. Test with valid habitat
    test_fishing(user_id, "갯벌")

    # 3. Test with another valid habitat
    test_fishing(user_id, "바다")

    # 4. Test with invalid habitat
    test_fishing(user_id, "우주")

if __name__ == "__main__":
    main()
