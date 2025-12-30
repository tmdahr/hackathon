import os
from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Get all species names from DB
all_species = db.query(Species).all()
species_names = set([s.name for s in all_species])

print(f"DB에 등록된 종: {len(species_names)}개\n")

# Get all sticker images from final_stickers
sticker_dir = "final_stickers"
sticker_files = [f for f in os.listdir(sticker_dir) if f.startswith('sticker_') and f.endswith('.png')]

print(f"final_stickers의 sticker_ 이미지: {len(sticker_files)}개\n")

# Find images without corresponding species
orphan_images = []

for sticker_file in sticker_files:
    # Extract species name from filename
    # e.g., sticker_갯게.png -> 갯게
    species_name = sticker_file.replace('sticker_', '').replace('.png', '')
    
    if species_name not in species_names:
        orphan_images.append((sticker_file, species_name))

print(f"DB에 등록되지 않은 이미지: {len(orphan_images)}개\n")

if orphan_images:
    for img_file, name in sorted(orphan_images):
        print(f"  - {img_file} (종 이름: {name})")
else:
    print("모든 sticker_ 이미지가 DB에 등록되어 있습니다!")

db.close()
