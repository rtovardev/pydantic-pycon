"""Acceso a PostgreSQL con asyncpg. Implementa el contrato Database de agente.py."""
import asyncpg


class PostgresDatabase:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def customer_plan(self, customer_id: int) -> str | None:
        return await self.pool.fetchval("SELECT plan FROM customers WHERE id = $1", customer_id)
