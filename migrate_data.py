from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Find all species with type 1
invasive_species = db.query(Species).filter(Species.type == 1).all()
print(f"Found {len(invasive_species)} species with Type 1 (Invasive). Migrating to Type 2 (Normal)...")

for s in invasive_species:
    s.type = 2

db.commit()
print("Migration complete.")
db.close()
