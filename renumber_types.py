from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Step 1: Migrate Type 2 (Normal) -> Type 1
normal_species = db.query(Species).filter(Species.type == 2).all()
print(f"Migrating {len(normal_species)} Normal species (Type 2 -> 1)...")
for s in normal_species:
    s.type = 1

# Step 2: Migrate Type 3 (Endangered) -> Type 2
endangered_species = db.query(Species).filter(Species.type == 3).all()
print(f"Migrating {len(endangered_species)} Endangered species (Type 3 -> 2)...")
for s in endangered_species:
    s.type = 2

db.commit()
print("Migration complete.")
db.close()
