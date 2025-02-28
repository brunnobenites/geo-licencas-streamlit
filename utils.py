# utils.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import pandas as pd
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

# Função assíncrona para carregar dados do banco de dados
async def carregar_dados():
    BASE_DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/")
    DB_NAME = os.getenv("DB_NAME", "licencas")
    DATABASE_URL = f"{BASE_DB_URL}{DB_NAME}"
    if not DATABASE_URL.startswith("postgresql+asyncpg://"):  # Alinhado e com :
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        query = text("SELECT * FROM licencas")
        result = await conn.execute(query)
        rows = result.fetchall()
        columns = result.keys()
    await engine.dispose()
    return pd.DataFrame(rows, columns=columns)