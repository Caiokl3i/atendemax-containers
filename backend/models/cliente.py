from pydantic import BaseModel, field_validator
from typing import Literal, Optional


class ClienteCreate(BaseModel):
    nome: str
    tipo: Literal["normal", "preferencial"]

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        nome = valor.strip()
        if not nome:
            raise ValueError("Nome não pode ser vazio")
        if len(nome) > 120:
            raise ValueError("Nome deve ter no máximo 120 caracteres")
        return nome


class ClienteResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    status: str
    posicao: Optional[int] = None
    horario_inicio: Optional[str] = None
    horario_conclusao: Optional[str] = None


class FilaResponse(BaseModel):
    total: int
    clientes: list[ClienteResponse]


class AcaoResponse(BaseModel):
    message: str
    cliente: Optional[ClienteResponse] = None
