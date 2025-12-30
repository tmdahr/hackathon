from app.database import SessionLocal
from app.models import Species

db = SessionLocal()
species = db.query(Species).order_by(Species.type, Species.name).all()

print(f"총 {len(species)}종이 등록되어 있습니다.\n")

type_map = {0: "쓰레기", 1: "일반 해양 생물", 2: "멸종위기종"}
current_type = -1

for s in species:
    if s.type != current_type:
        if current_type != -1:
            print("\n")
        current_type = s.type
        print(f"[{type_map.get(s.type, '기타')}]")
        print(f"  {s.name}", end="")
    else:
        print(f", {s.name}", end="")

print("\n")
db.close()
