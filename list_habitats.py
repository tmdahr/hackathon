from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Query distinct habitats
habitats = db.query(Species.habitat).distinct().all()
habitats = [h[0] for h in habitats]

print(f"Found {len(habitats)} unique habitats:")
print("-" * 30)
for h in habitats:
    print(h)

db.close()
