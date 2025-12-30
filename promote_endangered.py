from app.database import SessionLocal
from app.models import Species

db = SessionLocal()

target_names = ["남방큰돌고래", "상괭이", "점박이물범", "푸른바다거북", "대왕고래", "혹등고래", "매부리바다거북"]

print(f"Promoting the following to Endangered (Type 3): {target_names}")

count = 0
for name in target_names:
    species = db.query(Species).filter(Species.name == name).first()
    if species:
        species.type = 3
        count += 1
        print(f"Promoted: {name}")
    else:
        print(f"Not found: {name}")

db.commit()
print(f"Done. Promoted {count} species.")
db.close()
