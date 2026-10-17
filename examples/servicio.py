"""Servicio FastAPI que expone el agente con deadline y concurrencia acotada."""
import asyncio
import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from examples.agente import Database, Deps, Triage, agent
from examples.postgres import PostgresDatabase


class Ticket(BaseModel):
    text: str


def create_app(
    database: Database | None = None,
    model: str | None = None,
    deadline: float = 20.0,
    max_concurrent: int = 4,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        pool = None
        if database is None:
            pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])
            app.state.db = PostgresDatabase(pool)
        else:
            app.state.db = database
        app.state.slots = asyncio.Semaphore(max_concurrent)
        yield
        if pool is not None:
            await pool.close()

    app = FastAPI(lifespan=lifespan)

    @app.exception_handler(TimeoutError)
    async def plazo_superado(request: Request, exc: TimeoutError) -> JSONResponse:
        return JSONResponse(status_code=504, content={"detail": "El agente superó el plazo"})

    @app.post("/triage")
    async def triage(ticket: Ticket, request: Request) -> Triage:
        deps = Deps(db=request.app.state.db)
        async with request.app.state.slots, asyncio.timeout(deadline):
            result = await agent.run(ticket.text, deps=deps, model=model)
        return result.output

    return app
