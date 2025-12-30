from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Query species in '강, 호수'
target_habitat = "강, 호수"
species_list = db.query(Species).filter(Species.habitat == target_habitat).all()

print(f"Species found in habitat '{target_habitat}': {len(species_list)}")
print("-" * 50)
print(f"{'ID':<5} | {'Name':<20} | {'Type':<10}")
print("-" * 50)

for s in species_list:
    type_name = "Trash(0)" if s.type == 0 else "Normal(1)" if s.type == 1 else "Endangered(2)" if s.type == 2 else f"Unknown({s.type})"
    print(f"{s.id:<5} | {s.name:<20} | {type_name:<10}")

db.close()
