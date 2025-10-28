# app/storage/index_async.py
from pathlib import Path
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

class PhotoIndexAsync:
    """
    Async photo index for Postgres with OFFSET pagination.
    Schema expected:
        CREATE TABLE photos (
          seq BIGSERIAL PRIMARY KEY,
          uuid  TEXT NOT NULL UNIQUE,
          original_filename TEXT NOT NULL
        );
    """

    def __init__(self, database_url: str) -> None:
        # e.g. postgresql+asyncpg://app:secret@db:5432/photoindex
        self.engine: AsyncEngine = create_async_engine(database_url, future=True)

    async def reset_schema(self, schema_path: str) -> None:
        sql = Path(schema_path).read_text(encoding="utf-8")
        async with self.engine.begin() as conn:
            await conn.exec_driver_sql(sql)

    async def add(self, photo_id: str, original_filename: str) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(
                text("INSERT INTO photos (uuid, original_filename) VALUES (:id, :fn)"),
                {"id": photo_id, "fn": original_filename},
            )

    async def retrieve(self, n: int, page: int) -> List[str]:
        """
        OFFSET pagination (newest first):
          - page=1 -> items [0:n]
          - page=x -> items [(x-1)*n : (x-1)*n + n]
        """
        if n <= 0 or page <= 0:
            return []
        offset = (page - 1) * n
        async with self.engine.connect() as conn:
            rows = (await conn.execute(
                text(
                    "SELECT uuid FROM photos "
                    "ORDER BY seq DESC "
                    "LIMIT :limit OFFSET :offset"
                ),
                {"limit": n, "offset": offset},
            )).fetchall()
        return [r[0] for r in rows]

    async def count(self) -> int:
        async with self.engine.connect() as conn:
            (n,) = (await conn.execute(text("SELECT COUNT(*) FROM photos"))).one()
        return int(n)

    async def latest(self) -> Optional[str]:
        async with self.engine.connect() as conn:
            row = (await conn.execute(
                text("SELECT uuid FROM photos ORDER BY seq DESC LIMIT 1")
            )).fetchone()
        return row[0] if row else None

    async def delete(self, photo_id: str) -> bool:
        async with self.engine.begin() as conn:
            res = await conn.execute(
                text("DELETE FROM photos WHERE uuid = :id"),
                {"id": photo_id},
            )
        # res.rowcount is reliable with asyncpg
        return bool(getattr(res, "rowcount", 0))