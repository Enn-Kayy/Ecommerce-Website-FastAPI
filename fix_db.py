from app.database import Base, engine
from app import models

print("Dropping orders table if exists...")
models.Orders.__table__.drop(engine, checkfirst=True)

print("Recreating all tables...")
Base.metadata.create_all(bind=engine)

print("✅ DB Schema successfully updated!")
