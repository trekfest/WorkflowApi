from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Construct the database URL using the credentials from the config file
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Define a base class for declarative models
class Base(DeclarativeBase):
    pass

# Create an asynchronous database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session local factory with asynchronous support
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Function to create tables in the database asynchronously
async def create_tables():
    # Begin a transaction
    async with engine.begin() as conn:
        # Synchronize the creation of tables in the database
        await conn.run_sync(Base.metadata.create_all)



