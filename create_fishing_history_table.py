from app.database import engine
from sqlalchemy import text

# Create fishing_history table (MySQL syntax)
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fishing_history (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            user_id INTEGER NOT NULL,
            species_id INTEGER NOT NULL,
            caught_at VARCHAR(50),
            was_new BOOLEAN DEFAULT 0,
            invalidated BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (species_id) REFERENCES species(id)
        )
    """))
    conn.commit()
    print("fishing_history table created successfully!")
