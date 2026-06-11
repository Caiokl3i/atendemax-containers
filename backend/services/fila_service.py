from datetime import datetime, timezone

from sqlalchemy import case
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import Cliente
from models.cliente import ClienteCreate, ClienteResponse, FilaResponse

STATUS_NA_FILA = ("aguardando", "em_atendimento")
STATUS_HISTORICO = ("cancelado", "concluido")


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _formatar_horario(valor: datetime | None) -> str | None:
    if valor is None:
        return None
    return valor.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ordenacao_fila():
    prioridade_tipo = case(
        (Cliente.tipo == "preferencial", 0),
        else_=1,
    )
    return (prioridade_tipo, Cliente.data_criacao.asc())


def _para_response(
    cliente: Cliente, posicao: int | None = None
) -> ClienteResponse:
    return ClienteResponse(
        id=cliente.id,
        nome=cliente.nome,
        tipo=cliente.tipo,
        status=cliente.status,
        posicao=posicao,
        horario_inicio=_formatar_horario(cliente.horario_inicio),
        horario_conclusao=_formatar_horario(cliente.horario_conclusao),
    )


def _listar_fila_ordenada(db: Session) -> list[Cliente]:
    return (
        db.query(Cliente)
        .filter(Cliente.status.in_(STATUS_NA_FILA))
        .order_by(*_ordenacao_fila())
        .all()
    )


def _buscar_na_fila(db: Session, cliente_id: int) -> Cliente | None:
    return (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id, Cliente.status.in_(STATUS_NA_FILA))
        .first()
    )


def adicionar_cliente(dados_cliente: ClienteCreate) -> ClienteResponse:
    db = SessionLocal()
    try:
        cliente = Cliente(
            nome=dados_cliente.nome,
            tipo=dados_cliente.tipo,
            status="aguardando",
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        fila_ordenada = _listar_fila_ordenada(db)
        posicao = next(
            indice
            for indice, item in enumerate(fila_ordenada, start=1)
            if item.id == cliente.id
        )
        return _para_response(cliente, posicao)
    finally:
        db.close()


def obter_fila() -> FilaResponse:
    db = SessionLocal()
    try:
        clientes_db = _listar_fila_ordenada(db)
        clientes = [
            _para_response(cliente, indice)
            for indice, cliente in enumerate(clientes_db, start=1)
        ]
        return FilaResponse(total=len(clientes), clientes=clientes)
    finally:
        db.close()


def chamar_proximo() -> ClienteResponse:
    db = SessionLocal()
    try:
        fila = _listar_fila_ordenada(db)

        if any(cliente.status == "em_atendimento" for cliente in fila):
            raise ValueError("Já existe um cliente em atendimento.")

        proximo = next(
            (cliente for cliente in fila if cliente.status == "aguardando"),
            None,
        )
        if proximo is None:
            raise LookupError("Não há clientes aguardando na fila.")

        proximo.status = "em_atendimento"
        proximo.horario_inicio = _agora_utc()
        db.commit()
        db.refresh(proximo)

        posicao = fila.index(proximo) + 1
        return _para_response(proximo, posicao)
    finally:
        db.close()


def cancelar_cliente(cliente_id: int) -> None:
    db = SessionLocal()
    try:
        cliente = _buscar_na_fila(db, cliente_id)
        if cliente is None:
            raise LookupError("Cliente não encontrado.")

        if cliente.status != "aguardando":
            raise ValueError("Apenas clientes aguardando podem ser cancelados.")

        cliente.status = "cancelado"
        db.commit()
    finally:
        db.close()


def concluir_atendimento(cliente_id: int) -> None:
    db = SessionLocal()
    try:
        cliente = _buscar_na_fila(db, cliente_id)
        if cliente is None:
            raise LookupError("Cliente não encontrado.")

        if cliente.status != "em_atendimento":
            raise ValueError("Cliente não está em atendimento.")

        cliente.status = "concluido"
        cliente.horario_conclusao = _agora_utc()
        db.commit()
    finally:
        db.close()


def obter_historico(
    tipo: str | None = None,
    status: str | None = None,
) -> FilaResponse:
    db = SessionLocal()
    try:
        consulta = (
            db.query(Cliente)
            .filter(Cliente.status.in_(STATUS_HISTORICO))
            .order_by(Cliente.data_criacao.desc())
        )

        if tipo is not None:
            consulta = consulta.filter(Cliente.tipo == tipo)

        if status is not None:
            consulta = consulta.filter(Cliente.status == status)

        clientes_db = consulta.all()
        clientes = [_para_response(cliente) for cliente in clientes_db]
        return FilaResponse(total=len(clientes), clientes=clientes)
    finally:
        db.close()
