import asyncio

from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from examples.agente import agent
from examples.servicio import create_app


class FakeDb:
    async def customer_plan(self, customer_id: int) -> str | None:
        return "free"


def test_triage_devuelve_salida_validada():
    modelo = TestModel(
        call_tools=[],
        custom_output_args={"category": "acceso", "urgent": False, "needs_review": True, "summary": "Falta el correo"},
    )
    with agent.override(model=modelo), TestClient(create_app(database=FakeDb())) as client:
        response = client.post("/triage", json={"text": "No puedo entrar"})
    assert response.status_code == 200
    assert response.json() == {"category": "acceso", "urgent": False, "needs_review": True, "summary": "Falta el correo"}


def test_peticion_invalida_es_422():
    with TestClient(create_app(database=FakeDb())) as client:
        assert client.post("/triage", json={"texto": "x"}).status_code == 422


def test_deadline_devuelve_504():
    async def lento(messages, info):
        await asyncio.sleep(1)
        return ModelResponse(parts=[TextPart("tarde")])

    with agent.override(model=FunctionModel(lento)), TestClient(create_app(database=FakeDb(), deadline=0.05)) as client:
        assert client.post("/triage", json={"text": "hola"}).status_code == 504


class SinModelo:
    """Si el agente llega a llamar al modelo, la prueba falla."""

    def __call__(self, messages, info):
        raise AssertionError("no debió llamar al modelo")


def test_ticket_corto_es_422_sin_llamar_al_modelo():
    with agent.override(model=FunctionModel(SinModelo())), TestClient(create_app(database=FakeDb())) as client:
        assert client.post("/triage", json={"text": "   hola   "}).status_code == 422


def test_ticket_de_exactamente_10_caracteres_es_valido():
    modelo = TestModel(
        call_tools=[],
        custom_output_args={"category": "otro", "urgent": False, "needs_review": True, "summary": "Corto"},
    )
    with agent.override(model=modelo), TestClient(create_app(database=FakeDb())) as client:
        assert client.post("/triage", json={"text": "No funcion"}).status_code == 200


def test_ticket_largo_es_422():
    with agent.override(model=FunctionModel(SinModelo())), TestClient(create_app(database=FakeDb())) as client:
        assert client.post("/triage", json={"text": "x" * 2001}).status_code == 422
