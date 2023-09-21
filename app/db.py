from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

POSTGRES_SERVER = "db"
POSTGRES_PORT = "5432"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "azerty123"
POSTGRES_DB = "app"

engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
print(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
