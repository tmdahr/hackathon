import os
import shutil
import json
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Species

# Ensure tables exist (including the new column)
Base.metadata.create_all(bind=engine)

from sqlalchemy import text

def add_column_if_not_exists(engine, table_name, column_name, column_type):
    try:
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            conn.commit()
            print(f"Added column {column_name} to {table_name}")
    except Exception as e:
        # Ignore if column likely exists (OperationalError or similar)
        print(f"Column {column_name} might already exist or other error: {e}")

# Manually migrate schema
add_column_if_not_exists(engine, "species", "description", "VARCHAR(1000)")
add_column_if_not_exists(engine, "species", "habitat", "VARCHAR(50)")


def populate_db():
    db: Session = SessionLocal()
    
    archive_dir = "archive"
    stickers_dir = "final_stickers"
    static_images_dir = "app/static/images"
    
    # Get list of all JSON files
    try:
        json_files = [f for f in os.listdir(archive_dir) if f.endswith('.json')]
    except FileNotFoundError:
        print(f"Directory '{archive_dir}' not found.")
        return

    added_count = 0
    
    print(f"Found {len(json_files)} JSON files. processing...")
    
    for json_file in json_files:
        file_path = os.path.join(archive_dir, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            name = data.get('ovrLvbNm') # '저어새'
            if not name:
                print(f"Skipping {json_file}: Name not found in JSON")
                continue
                
            # Construct expected image filename: sticker_{name}.png
            # Note: The user mentioned sticker_가시닻해삼.png.
            # Filenames in macOS might have different normalization (NFC vs NFD), but python usually handles it well enough or we might need to normalize.
            # Let's try direct match first.
            
            image_filename = f"sticker_{name}.png"
            src_image_path = os.path.join(stickers_dir, image_filename)
            
            if not os.path.exists(src_image_path):
                # Try simple normalization or just skip
                # print(f"Image not found for {name}: {image_filename}")
                continue
                
            # Image exists!
            # 1. Copy image to static
            dst_image_path = os.path.join(static_images_dir, image_filename)
            shutil.copy2(src_image_path, dst_image_path)
            
            # 2. Check if species already exists
            existing_species = db.query(Species).filter(Species.name == name).first()
            
            description = data.get('ovrStleDstcftCn', '') + "\n\n" + data.get('ovrEcgyDstcftCn', '')
            description = description.strip()
            
            habitat = data.get('ovrHbttNm', '알 수 없음')
            
            if existing_species:
                # Update existing
                existing_species.description = description
                existing_species.habitat = habitat
                existing_species.image_url = f"/static/images/{image_filename}"
                print(f"Updated: {name}")
            else:
                # Create new
                new_species = Species(
                    name=name,
                    type=1, # Default type
                    price=100, # Default price
                    image_url=f"/static/images/{image_filename}",
                    habitat=habitat,
                    description=description
                )
                db.add(new_species)
                print(f"Added: {name}")
                
            added_count += 1
            
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    db.commit()
    db.close()
    print(f"Done. Successfully processed {added_count} species.")

if __name__ == "__main__":
    populate_db()
