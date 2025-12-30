from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

print("--- Added Trash (Type 0) ---")
trash = db.query(Species).filter(Species.type == 0).all()
for t in trash:
    print(f"- {t.name} (Price: {t.price})")

print("\n--- Added Invasive (Type 1) ---")
invasive = db.query(Species).filter(Species.type == 1).all()
for i in invasive:
    # Filter to show only the ones we likely added or unrelated ones if any
    # Just show first few
    print(f"- {i.name} (Price: {i.price})")
    
db.close()
