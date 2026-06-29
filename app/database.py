from typing import Dict, Any

_db: Dict[str, Any] = {
    "usuarios": {},
    "obras": {},
    "emprestimos": {},
    "reservas": {},
    "multas": {},
}

_counters: Dict[str, int] = {
    "usuario": 0,
    "obra": 0,
    "emprestimo": 0,
    "reserva": 0,
    "multa": 0,
}


def _next_id(entity: str) -> int:
    _counters[entity] += 1
    return _counters[entity]


def get_db() -> Dict[str, Any]:
    """
    Retorna o banco compartilhado com a função next_id injetada.
    Os repositórios recebem este dicionário via injeção de dependência.
    """
    return {**_db, "next_id": _next_id}