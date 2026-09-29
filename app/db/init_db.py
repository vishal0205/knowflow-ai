from sqlalchemy import text

from app.db.database import engine


def initialize_database():

    with engine.begin() as connection:

        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )

    print("pgvector extension enabled.")


if __name__ == "__main__":
    initialize_database()