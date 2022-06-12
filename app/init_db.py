from app.db.init_db import init_db
from app.db.session import SessionLocal


def init() -> None:
    db = SessionLocal()
    print("Seeding database...")
    init_db(db)
    print("DONE")


if __name__ == "__main__":
    init()
