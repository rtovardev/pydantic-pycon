"""Agente de triage de soporte con salida tipada. Datos sintéticos."""
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


class Database(Protocol):
    async def customer_plan(self, customer_id: int) -> str | None: ...


@dataclass
class Deps:
    db: Database


class Triage(BaseModel):
    category: Literal["facturacion", "acceso", "error", "otro"]
    urgent: bool
    needs_review: bool = Field(description="True si falta información")
    summary: str


agent = Agent(
    deps_type=Deps,
    output_type=Triage,
    instructions="Clasifica el ticket. Si falta información, marca needs_review.",
)


@agent.tool
async def customer_plan(ctx: RunContext[Deps], customer_id: int) -> str:
    """Devuelve el plan del cliente: free, pro o enterprise."""
    plan = await ctx.deps.db.customer_plan(customer_id)
    return plan or "desconocido"
