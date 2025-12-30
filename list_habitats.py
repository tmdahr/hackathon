from app.database import SessionLocal
from app.models import Species

db = SessionLocal()
habitats = db.query(Species.habitat).distinct().all()
print("Available Habitats:")
for h in habitats:
    print(h[0])
db.close()
