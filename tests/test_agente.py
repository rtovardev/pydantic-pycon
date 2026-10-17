import pytest
from pydantic_ai.models.test import TestModel

from examples.agente import Deps, Triage, agent


class FakeDb:
    def __init__(self):
        self.asked: list[int] = []

    async def customer_plan(self, customer_id: int) -> str | None:
        self.asked.append(customer_id)
        return "pro"


async def test_salida_tipada_y_tool():
    db = FakeDb()
    modelo = TestModel(
        call_tools=["customer_plan"],
        custom_output_args={"category": "facturacion", "urgent": True, "needs_review": False, "summary": "Cobro doble"},
    )
    with agent.override(model=modelo):
        result = await agent.run("Me cobraron dos veces", deps=Deps(db=db))
    assert result.output == Triage(category="facturacion", urgent=True, needs_review=False, summary="Cobro doble")
    assert db.asked, "la tool debió consultar la base"


async def test_categoria_invalida_no_pasa_la_validacion():
    modelo = TestModel(
        call_tools=[],
        custom_output_args={"category": "magia", "urgent": False, "needs_review": False, "summary": "x"},
    )
    with agent.override(model=modelo):
        with pytest.raises(Exception):
            await agent.run("hola", deps=Deps(db=FakeDb()))
