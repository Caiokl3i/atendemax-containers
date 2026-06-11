from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, Optional
import uvicorn

from database.database import Base, engine
from database import models 
from models.cliente import AcaoResponse, ClienteCreate, FilaResponse
from services.fila_service import (
    adicionar_cliente,
    cancelar_cliente,
    chamar_proximo,
    concluir_atendimento,
    obter_fila,
    obter_historico,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.get("/fila", response_model=FilaResponse)
def listar_fila():
    return obter_fila()


@app.post("/clientes", status_code=status.HTTP_201_CREATED, response_model=AcaoResponse)
def criar_cliente(dados_cliente: ClienteCreate):
    cliente = adicionar_cliente(dados_cliente)
    return AcaoResponse(
        message="Cliente adicionado à fila com sucesso.",
        cliente=cliente,
    )


@app.post("/fila/chamar", response_model=AcaoResponse)
def chamar_proximo_cliente():
    try:
        cliente = chamar_proximo()
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))
    except LookupError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))

    return AcaoResponse(
        message="Próximo cliente chamado com sucesso.",
        cliente=cliente,
    )


@app.delete("/clientes/{cliente_id}", response_model=AcaoResponse)
def cancelar_cliente_endpoint(cliente_id: int):
    try:
        cancelar_cliente(cliente_id)
    except LookupError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return AcaoResponse(message="Cliente cancelado com sucesso.")


@app.post("/atendimentos/{cliente_id}/concluir", response_model=AcaoResponse)
def concluir_atendimento_endpoint(cliente_id: int):
    try:
        concluir_atendimento(cliente_id)
    except LookupError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return AcaoResponse(message="Atendimento concluído com sucesso.")


@app.get("/historico", response_model=FilaResponse)
def listar_historico(
    tipo: Optional[Literal["normal", "preferencial"]] = Query(default=None),
    status_filtro: Optional[Literal["cancelado", "concluido"]] = Query(
        default=None, alias="status"
    ),
):
    return obter_historico(tipo=tipo, status=status_filtro)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
