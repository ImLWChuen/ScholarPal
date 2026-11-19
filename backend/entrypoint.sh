#!/bin/sh
set -e

echo "==> Starting ScholarPal Backend service..."

# Wait for database availability
echo "==> Checking database connection..."
python -c "
import asyncio, sys, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def check():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        print('==> Database connection successful!')
        sys.exit(0)
    except Exception as e:
        print(f'==> Database not ready yet: {e}')
        sys.exit(1)

asyncio.run(check())
" || {
    echo "==> Waiting 3 seconds for database..."
    sleep 3
}

# Run database migrations if enabled
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "==> Running database migrations via Alembic..."
    alembic upgrade head
fi

# Run seed data if enabled
if [ "$SEED_DATA" = "true" ]; then
    echo "==> Seeding initial scholarship data..."
    python -m app.core.seed
fi

echo "==> Launching FastAPI application via Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
