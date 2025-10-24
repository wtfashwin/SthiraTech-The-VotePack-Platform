from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from . import config 

engine = create_engine(config.settings.DATABASE_URL)

@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    """
    On the very first connection to a new database, this function will execute
    the 'CREATE EXTENSION IF NOT EXISTS vector' command. This ensures that
    the pgvector extension is always enabled, making the app robust.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    finally:
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

