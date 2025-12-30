from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Check if trash exists
trash = db.query(Species).filter(Species.type == 0).first()
if not trash:
    print("No trash found. Creating 'Old Boot'...")
    new_trash = Species(
        name="낡은 장화",
        type=0,
        price=0,
        image_url="/static/images/trash_boot.png", # Placeholder
        habitat="모름",
        description="누군가 버린 장화입니다."
    )
    db.add(new_trash)
    db.commit()
    print("Trash created.")
else:
    print(f"Trash exists: {trash.name}")

db.close()
