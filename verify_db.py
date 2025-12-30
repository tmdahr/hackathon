from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Species
import os

def verify():
    db: Session = SessionLocal()
    
    # List top 20 species
    all_species = db.query(Species).limit(20).all()
    print(f"Total found: {db.query(Species).count()}")
    for s in all_species:
        print(f"- {s.name} : {s.image_url}")

    db.close()

if __name__ == "__main__":
    verify()
