from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar("T")


# Interface Base (Repository Pattern)

class BaseRepository(ABC, Generic[T]):
    """Contrato genérico que todo repositório concreto deve implementar."""

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


# Repositório de Usuários

class UsuarioRepository(BaseRepository):
    def __init__(self, db: Dict[str, Any]):
        self._store = db["usuarios"]
        self._next_id = db["next_id"]

    def criar(self, dados: dict) -> dict:
        id_ = self._next_id("usuario")
        usuario = {"id": id_, **dados}
        self._store[id_] = usuario
        return usuario

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return self._store.get(id)

    def buscar_por_matricula(self, matricula: str) -> Optional[dict]:
        return next((u for u in self._store.values() if u["matricula"] == matricula), None)

    def listar_todos(self) -> List[dict]:
        return list(self._store.values())

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        if id not in self._store:
            return None
        self._store[id].update(dados)
        return self._store[id]

    def deletar(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True


# Repositório de Obras
class ObraRepository(BaseRepository):
    def __init__(self, db: Dict[str, Any]):
        self._store = db["obras"]
        self._next_id = db["next_id"]

    def criar(self, dados: dict) -> dict:
        id_ = self._next_id("obra")
        obra = {"id": id_, **dados}
        self._store[id_] = obra
        return obra

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return self._store.get(id)

    def listar_todos(self) -> List[dict]:
        return list(self._store.values())

    def listar_disponiveis(self) -> List[dict]:
        return [o for o in self._store.values() if o["quantidade_disponivel"] > 0]

    def listar_bestsellers(self) -> List[dict]:
        return [o for o in self._store.values() if o.get("eh_bestseller")]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        if id not in self._store:
            return None
        self._store[id].update(dados)
        return self._store[id]

    def deletar(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True

    def decrementar_quantidade(self, id: int) -> bool:
        obra = self._store.get(id)
        if not obra or obra["quantidade_disponivel"] <= 0:
            return False
        obra["quantidade_disponivel"] -= 1
        return True

    def incrementar_quantidade(self, id: int) -> bool:
        obra = self._store.get(id)
        if not obra:
            return False
        obra["quantidade_disponivel"] += 1
        return True


# Repositório de Empréstimos
class EmprestimoRepository(BaseRepository):
    def __init__(self, db: Dict[str, Any]):
        self._store = db["emprestimos"]
        self._next_id = db["next_id"]

    def criar(self, dados: dict) -> dict:
        id_ = self._next_id("emprestimo")
        emprestimo = {"id": id_, "data_devolucao": None, "status": "Ativo", **dados}
        self._store[id_] = emprestimo
        return emprestimo

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return self._store.get(id)

    def listar_todos(self) -> List[dict]:
        return list(self._store.values())

    def listar_por_usuario(self, usuario_id: int) -> List[dict]:
        return [e for e in self._store.values() if e["usuario_id"] == usuario_id]

    def listar_ativos_por_usuario(self, usuario_id: int) -> List[dict]:
        return [
            e for e in self._store.values()
            if e["usuario_id"] == usuario_id and e["status"] == "Ativo"
        ]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        if id not in self._store:
            return None
        self._store[id].update(dados)
        return self._store[id]

    def deletar(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True


# Repositório de Reservas
class ReservaRepository(BaseRepository):
    def __init__(self, db: Dict[str, Any]):
        self._store = db["reservas"]
        self._next_id = db["next_id"]

    def criar(self, dados: dict) -> dict:
        id_ = self._next_id("reserva")
        reserva = {"id": id_, **dados}
        self._store[id_] = reserva
        return reserva

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return self._store.get(id)

    def listar_todos(self) -> List[dict]:
        return list(self._store.values())

    def listar_fila_por_obra(self, obra_id: int) -> List[dict]:
        """Retorna a fila de uma obra ordenada por posição (RF02)."""
        fila = [r for r in self._store.values() if r["obra_id"] == obra_id]
        return sorted(fila, key=lambda r: r["posicao_fila"])

    def proxima_posicao_na_fila(self, obra_id: int) -> int:
        fila = self.listar_fila_por_obra(obra_id)
        return (fila[-1]["posicao_fila"] + 1) if fila else 1

    def remover_primeiro_da_fila(self, obra_id: int) -> Optional[dict]:
        fila = self.listar_fila_por_obra(obra_id)
        if not fila:
            return None
        primeiro = fila[0]
        del self._store[primeiro["id"]]
        return primeiro

    def usuario_ja_reservou(self, usuario_id: int, obra_id: int) -> bool:
        return any(
            r["usuario_id"] == usuario_id and r["obra_id"] == obra_id
            for r in self._store.values()
        )

    def listar_por_usuario(self, usuario_id: int) -> List[dict]:
        return [r for r in self._store.values() if r["usuario_id"] == usuario_id]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        if id not in self._store:
            return None
        self._store[id].update(dados)
        return self._store[id]

    def deletar(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True


# Repositório de Multas
class MultaRepository(BaseRepository):
    def __init__(self, db: Dict[str, Any]):
        self._store = db["multas"]
        self._next_id = db["next_id"]

    def criar(self, dados: dict) -> dict:
        id_ = self._next_id("multa")
        multa = {"id": id_, "paga": False, **dados}
        self._store[id_] = multa
        return multa

    def buscar_por_id(self, id: int) -> Optional[dict]:
        return self._store.get(id)

    def listar_todos(self) -> List[dict]:
        return list(self._store.values())

    def listar_pendentes_por_usuario(self, usuario_id: int, emprestimos: list) -> List[dict]:
        """Retorna multas não pagas dos empréstimos do usuário."""
        ids_emp = {e["id"] for e in emprestimos}
        return [
            m for m in self._store.values()
            if m["emprestimo_id"] in ids_emp and not m["paga"]
        ]

    def atualizar(self, id: int, dados: dict) -> Optional[dict]:
        if id not in self._store:
            return None
        self._store[id].update(dados)
        return self._store[id]

    def deletar(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True