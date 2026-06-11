from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora_utc, nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="aguardando", nullable=False)
    horario_inicio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    horario_conclusao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
