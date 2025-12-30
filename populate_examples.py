from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# 0: Trash, 1: Invasive, 2: Normal, 3: Endangered

items = [
    # Trash (Type 0)
    {
        "name": "폐타이어",
        "type": 0,
        "price": 0,
        "habitat": "모름",
        "image_url": "/static/images/trash_tire.png",
        "description": "바다에 버려진 낡은 타이어입니다. 환경오염의 주범입니다."
    },
    {
        "name": "플라스틱 병",
        "type": 0,
        "price": 0,
        "habitat": "모름",
        "image_url": "/static/images/trash_bottle.png",
        "description": "분해되는 데 수백 년이 걸리는 플라스틱 병입니다."
    },
    {
        "name": "찌그러진 캔",
        "type": 0,
        "price": 0,
        "habitat": "모름",
        "image_url": "/static/images/trash_can.png",
        "description": "누군가 마시고 버린 빈 캔입니다."
    },
    # Invasive (Type 1)
    {
        "name": "큰입배스",
        "type": 1,
        "price": 200,
        "habitat": "강, 호수", # Freshwater usually, but allowing for game logic
        "image_url": "/static/images/fish_bass.png",
        "description": "토종 물고기를 잡아먹는 생태계 교란종입니다."
    },
    {
        "name": "파랑볼우럭(블루길)",
        "type": 1,
        "price": 150,
        "habitat": "강, 호수",
        "image_url": "/static/images/fish_bluegill.png",
        "description": "번식력이 강해 토종 생태계를 위협합니다."
    },
    {
        "name": "붉은귀거북",
        "type": 1,
        "price": 300,
        "habitat": "강, 호수",
        "image_url": "/static/images/fish_turtle.png",
        "description": "잡식성으로 남생이의 서식지를 위협합니다."
    }
]

print("Starting population...")
for item in items:
    exists = db.query(Species).filter(Species.name == item["name"]).first()
    if exists:
        print(f"Skipping {item['name']} (Already exists)")
    else:
        new_species = Species(**item)
        db.add(new_species)
        print(f"Added {item['name']} ({'Trash' if item['type']==0 else 'Invasive'})")

db.commit()
db.close()
print("Done.")
