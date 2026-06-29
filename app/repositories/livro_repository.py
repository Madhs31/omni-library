from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Generic, TypeVar, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm_models import (
    UsuarioORM,
    ObraORM,
    EmprestimoORM,
    ReservaORM,
    MultaORM,
)

T = TypeVar("T")


def _normalizar_valor(valor):
    if isinstance(valor, Enum):
        return valor.value
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except ValueError:
            return valor
    return valor


def _normalizar_dados(dados: dict) -> dict:
    return {chave: _normalizar_valor(valor) for chave, valor in dados.items()}


def _serializar(obj) -> Optional[dict]:
    if obj is None:
        return None

    dados = {}
    for coluna in obj.__table__.columns:
        valor = getattr(obj, coluna.name)
        if isinstance(valor, date):
            valor = valor.isoformat()
        dados[coluna.name] = valor
    return dados


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def criar(self, dados: dict) -> T: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[T]: ...

    @abstractmethod
    def listar_todos(self) -> List[T]: ...

    @abstractmethod
    def atualizar(self, id: int, dados: dict) -> Optional[T]: ...

    @abstractmethod
    def deletar(self, id: int) -> bool: ...


class UsuarioRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> dict:
        usuario = UsuarioORM(**_normalizar_dados(dados))
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return _serializar(usuario)

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return _serializar(self.db.get(UsuarioORM, id))

    def buscar_por_matricula(self, matricula: str) -> Optional[dict]:
        usuario = self.db.scalar(select(UsuarioORM).where(UsuarioORM.matricula == matricula))
        return _serializar(usuario)

    def listar_todos(self) -> List[dict]:
        return [_serializar(u) for u in self.db.scalars(select(UsuarioORM)).all()]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        usuario = self.db.get(UsuarioORM, id)
        if not usuario:
            return None
        for chave, valor in _normalizar_dados(dados).items():
            setattr(usuario, chave, valor)
        self.db.commit()
        self.db.refresh(usuario)
        return _serializar(usuario)

    def deletar(self, id: int) -> bool:
        usuario = self.db.get(UsuarioORM, id)
        if not usuario:
            return False
        self.db.delete(usuario)
        self.db.commit()
        return True


class ObraRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> dict:
        obra = ObraORM(**_normalizar_dados(dados))
        self.db.add(obra)
        self.db.commit()
        self.db.refresh(obra)
        return _serializar(obra)

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return _serializar(self.db.get(ObraORM, id))

    def listar_todos(self) -> List[dict]:
        return [_serializar(o) for o in self.db.scalars(select(ObraORM)).all()]

    def listar_disponiveis(self) -> List[dict]:
        obras = self.db.scalars(select(ObraORM).where(ObraORM.quantidade_disponivel > 0)).all()
        return [_serializar(o) for o in obras]

    def listar_bestsellers(self) -> List[dict]:
        obras = self.db.scalars(select(ObraORM).where(ObraORM.eh_bestseller.is_(True))).all()
        return [_serializar(o) for o in obras]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        obra = self.db.get(ObraORM, id)
        if not obra:
            return None
        for chave, valor in _normalizar_dados(dados).items():
            setattr(obra, chave, valor)
        self.db.commit()
        self.db.refresh(obra)
        return _serializar(obra)

    def deletar(self, id: int) -> bool:
        obra = self.db.get(ObraORM, id)
        if not obra:
            return False
        self.db.delete(obra)
        self.db.commit()
        return True

    def decrementar_quantidade(self, id: int) -> bool:
        obra = self.db.get(ObraORM, id)
        if not obra or obra.quantidade_disponivel <= 0:
            return False
        obra.quantidade_disponivel -= 1
        self.db.commit()
        return True

    def incrementar_quantidade(self, id: int) -> bool:
        obra = self.db.get(ObraORM, id)
        if not obra:
            return False
        obra.quantidade_disponivel += 1
        self.db.commit()
        return True


class EmprestimoRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> dict:
        dados = {"data_devolucao": None, "status": "Ativo", **dados}
        emprestimo = EmprestimoORM(**_normalizar_dados(dados))
        self.db.add(emprestimo)
        self.db.commit()
        self.db.refresh(emprestimo)
        return _serializar(emprestimo)

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return _serializar(self.db.get(EmprestimoORM, id))

    def listar_todos(self) -> List[dict]:
        return [_serializar(e) for e in self.db.scalars(select(EmprestimoORM)).all()]

    def listar_por_usuario(self, usuario_id: int) -> List[dict]:
        itens = self.db.scalars(select(EmprestimoORM).where(EmprestimoORM.usuario_id == usuario_id)).all()
        return [_serializar(e) for e in itens]

    def listar_ativos_por_usuario(self, usuario_id: int) -> List[dict]:
        itens = self.db.scalars(
            select(EmprestimoORM).where(
                EmprestimoORM.usuario_id == usuario_id,
                EmprestimoORM.status == "Ativo",
            )
        ).all()
        return [_serializar(e) for e in itens]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        emprestimo = self.db.get(EmprestimoORM, id)
        if not emprestimo:
            return None
        for chave, valor in _normalizar_dados(dados).items():
            setattr(emprestimo, chave, valor)
        self.db.commit()
        self.db.refresh(emprestimo)
        return _serializar(emprestimo)

    def deletar(self, id: int) -> bool:
        emprestimo = self.db.get(EmprestimoORM, id)
        if not emprestimo:
            return False
        self.db.delete(emprestimo)
        self.db.commit()
        return True


class ReservaRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> dict:
        reserva = ReservaORM(**_normalizar_dados(dados))
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return _serializar(reserva)

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return _serializar(self.db.get(ReservaORM, id))

    def listar_todos(self) -> List[dict]:
        return [_serializar(r) for r in self.db.scalars(select(ReservaORM)).all()]

    def listar_fila_por_obra(self, obra_id: int) -> List[dict]:
        reservas = self.db.scalars(
            select(ReservaORM)
            .where(ReservaORM.obra_id == obra_id)
            .order_by(ReservaORM.posicao_fila)
        ).all()
        return [_serializar(r) for r in reservas]

    def proxima_posicao_na_fila(self, obra_id: int) -> int:
        fila = self.listar_fila_por_obra(obra_id)
        return fila[-1]["posicao_fila"] + 1 if fila else 1

    def remover_primeiro_da_fila(self, obra_id: int) -> Optional[dict]:
        reserva = self.db.scalar(
            select(ReservaORM)
            .where(ReservaORM.obra_id == obra_id)
            .order_by(ReservaORM.posicao_fila)
        )
        if not reserva:
            return None
        dados = _serializar(reserva)
        self.db.delete(reserva)
        self.db.commit()
        return dados

    def usuario_ja_reservou(self, usuario_id: int, obra_id: int) -> bool:
        reserva = self.db.scalar(
            select(ReservaORM).where(
                ReservaORM.usuario_id == usuario_id,
                ReservaORM.obra_id == obra_id,
            )
        )
        return reserva is not None

    def listar_por_usuario(self, usuario_id: int) -> List[dict]:
        reservas = self.db.scalars(select(ReservaORM).where(ReservaORM.usuario_id == usuario_id)).all()
        return [_serializar(r) for r in reservas]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        reserva = self.db.get(ReservaORM, id)
        if not reserva:
            return None
        for chave, valor in _normalizar_dados(dados).items():
            setattr(reserva, chave, valor)
        self.db.commit()
        self.db.refresh(reserva)
        return _serializar(reserva)

    def deletar(self, id: int) -> bool:
        reserva = self.db.get(ReservaORM, id)
        if not reserva:
            return False
        self.db.delete(reserva)
        self.db.commit()
        return True


class MultaRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> dict:
        dados = {"paga": False, **dados}
        multa = MultaORM(**_normalizar_dados(dados))
        self.db.add(multa)
        self.db.commit()
        self.db.refresh(multa)
        return _serializar(multa)

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return _serializar(self.db.get(MultaORM, id))

    def listar_todos(self) -> List[dict]:
        return [_serializar(m) for m in self.db.scalars(select(MultaORM)).all()]

    def listar_pendentes_por_usuario(self, usuario_id: int, emprestimos: list) -> List[dict]:
        ids_emp = {e["id"] for e in emprestimos}
        if not ids_emp:
            return []
        multas = self.db.scalars(
            select(MultaORM).where(
                MultaORM.emprestimo_id.in_(ids_emp),
                MultaORM.paga.is_(False),
            )
        ).all()
        return [_serializar(m) for m in multas]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        multa = self.db.get(MultaORM, id)
        if not multa:
            return None
        for chave, valor in _normalizar_dados(dados).items():
            setattr(multa, chave, valor)
        self.db.commit()
        self.db.refresh(multa)
        return _serializar(multa)

    def deletar(self, id: int) -> bool:
        multa = self.db.get(MultaORM, id)
        if not multa:
            return False
        self.db.delete(multa)
        self.db.commit()
        return True