from app.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.id == 5).first()
if user:
    user.pollution_level = 100
    db.commit()
    print(f"User {user.id} pollution set to {user.pollution_level}")
else:
    print("User 5 not found")
db.close()
