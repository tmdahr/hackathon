from app.database import SessionLocal
from app.models import Species
import os

db = SessionLocal()

# Get all Trash species (type=0)
trash_items = db.query(Species).filter(Species.type == 0).all()

print(f"Found {len(trash_items)} trash items:")
print("-" * 60)
print(f"{'Name':<15} | {'Image URL':<35} | {'Exists?'}")
print("-" * 60)

static_dir = "app/static" # relative to project root

for item in trash_items:
    # URL is like /static/images/filename.png
    # We need to convert it to local path: app/static/images/filename.png
    relative_path = item.image_url.lstrip("/") 
    full_path = os.path.join(os.getcwd(), relative_path)
    
    exists = os.path.exists(full_path)
    print(f"{item.name:<15} | {item.image_url:<35} | {exists}")

db.close()
