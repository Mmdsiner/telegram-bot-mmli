import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")

# حل مشکل Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:

        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            price_normal TEXT,
            price_vip TEXT,
            card TEXT,
            mode TEXT
        )
        """))

        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            product TEXT,
            price TEXT,
            status TEXT
        )
        """))

        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS discounts (
            code TEXT PRIMARY KEY,
            type TEXT,
            value INT
        )
        """))

        res = await conn.execute(text("SELECT * FROM settings"))
        if not res.first():
            await conn.execute(text("""
            INSERT INTO settings (price_normal, price_vip, card, mode)
            VALUES ('50000','80000','----','fixed')
            """))

async def get_settings():
    async with SessionLocal() as s:
        r = await s.execute(text("SELECT * FROM settings LIMIT 1"))
        return dict(r.first()._mapping)

async def update_setting(key, value):
    async with SessionLocal() as s:
        await s.execute(text(f"UPDATE settings SET {key}=:v"), {"v": value})
        await s.commit()

async def create_order(user_id, product, price):
    async with SessionLocal() as s:
        r = await s.execute(text("""
        INSERT INTO orders (user_id,product,price,status)
        VALUES (:u,:p,:pr,'pending') RETURNING id
        """), {"u":user_id,"p":product,"pr":price})
        await s.commit()
        return r.scalar()

async def get_orders():
    async with SessionLocal() as s:
        r = await s.execute(text("SELECT * FROM orders"))
        return [dict(x._mapping) for x in r]

async def update_order(order_id, status):
    async with SessionLocal() as s:
        await s.execute(text("UPDATE orders SET status=:s WHERE id=:id"),
                        {"s":status,"id":order_id})
        r = await s.execute(text("SELECT * FROM orders WHERE id=:id"),
                            {"id":order_id})
        await s.commit()
        return dict(r.first()._mapping)
