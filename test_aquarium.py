import requests

base_url = "http://localhost:8000"
user_id = 12  # 임시테스트 유저

# 1. 낚시 결과가 있다고 가정하고 수족관 액션 호출
# 실제로 낚은 적 있는 달랑게(32)나 다른 종을 사용해야 하나, 
# 여기서는 DB에 있는 특정 종으로 테스트
species_id = 74  # 가시해마

action_data = {
    "user_id": user_id,
    "species_id": species_id,
    "action": "AQUARIUM"
}

print("Testing AQUARIUM action...")
resp = requests.post(f"{base_url}/game/action", json=action_data)
if resp.status_code == 200:
    print("Action successful:", resp.json()["message"])
else:
    print("Action failed:", resp.status_code, resp.text)

# 2. 아쿠아리움 목록 조회
print("\nChecking Aquarium list...")
resp = requests.get(f"{base_url}/aquarium/{user_id}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Nickname: {data['nickname']}")
    print(f"Fish count: {len(data['fish_list'])}")
    for fish in data['fish_list']:
        print(f"  - {fish['name']} (caught at {fish['caught_at']})")
else:
    print("List lookup failed:", resp.status_code, resp.text)
