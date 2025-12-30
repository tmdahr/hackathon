import os
from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

# Get all species and their image filenames (from sticker_ pattern)
all_species = db.query(Species).all()
used_sticker_names = set()

for species in all_species:
    if species.image_url:
        filename = os.path.basename(species.image_url)
        # For species with sticker_ prefix, extract the name
        if filename.startswith('sticker_'):
            # e.g., sticker_갯게.png from /static/images/sticker_갯게.png
            used_sticker_names.add(filename)
        else:
            # For trash items like trash_tire.png, we don't count them
            pass

print(f"DB에서 사용중인 sticker_ 이미지: {len(used_sticker_names)}개")

# Get all sticker_ PNG files in final_stickers (excluding trash images)
sticker_dir = "final_stickers"
all_stickers = set([f for f in os.listdir(sticker_dir) 
                    if f.endswith('.png') and f.startswith('sticker_')])

print(f"final_stickers 폴더의 sticker_ 이미지: {len(all_stickers)}개")

# Find unused images
unused_images = all_stickers - used_sticker_names

print(f"\n사용되지 않는 sticker_ 이미지: {len(unused_images)}개\n")

for img in sorted(unused_images):
    # Extract species name
    name = img.replace('sticker_', '').replace('.png', '')
    print(f"  - {img} ({name})")

# Also show non-sticker images
other_images = set([f for f in os.listdir(sticker_dir) 
                   if f.endswith('.png') and not f.startswith('sticker_')])
print(f"\n기타 이미지 ({len(other_images)}개):")
for img in sorted(other_images):
    print(f"  - {img}")

db.close()
