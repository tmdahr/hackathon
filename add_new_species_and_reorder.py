import json
from app.database import SessionLocal, engine
from app.models import Species, Collection, FishingHistory
from sqlalchemy import text

db = SessionLocal()

def update_db():
    # 1. Shift Trash IDs (74-77 -> 76-79)
    # We need to do this carefully to avoid primary key conflicts.
    # Also need to update collections and fishing_history tables.
    
    trash_ids = [77, 76, 75, 74] # Descending order to avoid immediate conflict if handled one by one, 
    # but since it's a batch we can use SQL.
    
    print("Shifting Trash IDs...")
    try:
        with engine.connect() as conn:
            # Disable FK checks for MySQL
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            for old_id in trash_ids:
                new_id = old_id + 2
                print(f"  Moving {old_id} -> {new_id}")
                
                # Update Species ID
                conn.execute(text("UPDATE species SET id = :new_id WHERE id = :old_id"), {"new_id": new_id, "old_id": old_id})
                
                # Update Collection
                conn.execute(text("UPDATE collections SET species_id = :new_id WHERE species_id = :old_id"), {"new_id": new_id, "old_id": old_id})
                
                # Update FishingHistory
                conn.execute(text("UPDATE fishing_history SET species_id = :new_id WHERE species_id = :old_id"), {"new_id": new_id, "old_id": old_id})
            
            # Re-enable FK checks
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
            print("Trash IDs shifted successfully.")
    except Exception as e:
        print(f"Error shifting IDs: {e}")
        db.rollback()
        return

    # 2. Insert New Species
    print("Inserting new species...")
    
    new_items = [
        {
            "id": 74,
            "name": "가시해마",
            "type": 2, # Endangered (멸종위기종)
            "price": 100,
            "habitat": "바다숲",
            "image_url": "/static/images/sticker_가시해마.png",
            "description": "우리나라에 서식하는 해마 중 가장 두드러진 가시를 가지며, 가시의 끝은 갈라져 있습니다. 주둥이는 비교적 길며, 띠를 가집니다."
        },
        {
            "id": 75,
            "name": "대추귀고동",
            "type": 1, # Normal (일반 해양 생물)
            "price": 100,
            "habitat": "하구역",
            "image_url": "/static/images/sticker_대추귀고동.png",
            "description": "세로 길이 3.5cm, 가로 길이 1.7cm 정도의 껍질을 가지며, 긴 달걀모양으로 전체적으로 대추 모양을 하고 있습니다. 밀물 때 바닷물과 맞닿는 갯벌의 윗 부분 중에서도 갯 잔디가 있는 지역에 서식합니다."
        }
    ]
    
    for item in new_items:
        exists = db.query(Species).filter(Species.id == item["id"]).first()
        if exists:
            print(f"  Species with ID {item['id']} already exists! ({exists.name})")
        else:
            new_s = Species(**item)
            db.add(new_s)
            print(f"  Added: {item['name']} (ID: {item['id']})")
    
    db.commit()
    print("Database update complete.")

if __name__ == "__main__":
    update_db()
    db.close()
