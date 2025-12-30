import requests
from app.models import Species, User

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

def generate_message(species: Species, user: User) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {
            "fish_name": species.name,
            "user_name": user.nickname,
            "feature": species.description,
            "protection": species.type, 
            "pollution_level": str(user.pollution_level)
        },
        "response_mode": "blocking",
        "user": f"user-{user.id}"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "편지를 쓸 수 없어요.")
    except Exception as e:
        print(f"Error generating message: {e}")
        return "편지를 쓰는 도중 문제가 발생했어요."