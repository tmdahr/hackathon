from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

target_names = ["큰입배스", "파랑볼우럭(블루길)", "붉은귀거북"]

print(f"Deleting the following legacy species: {target_names}")

count = 0
for name in target_names:
    species = db.query(Species).filter(Species.name == name).first()
    if species:
        db.delete(species)
        count += 1
        print(f"Deleted: {name}")
    else:
        print(f"Not found: {name}")

db.commit()
print(f"Done. Deleted {count} species.")
db.close()
