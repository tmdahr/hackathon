from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Query all species
all_species = db.query(Species).order_by(Species.type, Species.id).all()

print(f"총 {len(all_species)}종의 해양 생물이 등록되어 있습니다.\n")
print(f"{'ID':<5} | {'이름':<20} | {'타입':<15} | {'가격':<8} | {'서식지':<15}")
print("-" * 80)

type_names = {0: "쓰레기", 1: "일반 해양 생물", 2: "멸종위기종"}

for species in all_species:
    type_name = type_names.get(species.type, "기타")
    print(f"{species.id:<5} | {species.name:<20} | {type_name:<15} | {species.price:<8} | {species.habitat:<15}")

db.close()
