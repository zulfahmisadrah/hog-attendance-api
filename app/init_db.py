from app.db.init_db import init_db
from app.db.session import SessionLocal


def init() -> None:
    db = SessionLocal()
    print("Create initial data")
    init_db(db)
    print("Initial data created")


if __name__ == "__main__":
    init()
