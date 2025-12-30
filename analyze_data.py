from app.database import SessionLocal
from app.models import Species
from sqlalchemy import func

db = SessionLocal()

# Count species by habitat and type
results = db.query(
    Species.habitat, 
    Species.type, 
    func.count(Species.id)
).group_by(Species.habitat, Species.type).all()

# Output results
print(f"{'Habitat':<20} | {'Type':<10} | {'Count':<5}")
print("-" * 40)
for habitat, type_code, count in results:
    type_name = "Trash" if type_code == 0 else "Normal" if type_code == 1 else "Endangered" if type_code == 2 else f"Unknown({type_code})"
    print(f"{habitat:<20} | {type_name:<10} | {count:<5}")

db.close()
