import requests

url = "http://localhost:8000/users/"
nickname = "임시테스트"

# Try to register the same name twice
response1 = requests.post(url, json={"nickname": nickname})
print(f"Response (should be user 12): {response1.status_code}")
print(response1.json())

# Just in case, confirm with another "new" name to see it still works
new_nickname = "테스트유저2"
response2 = requests.post(url, json={"nickname": new_nickname})
# Since this might fail if it already exists from previous runs, we just check if it's 200
print(f"Response for new user: {response2.status_code}")
print(response2.json())
