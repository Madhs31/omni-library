"""
Models — entidades de domínio do sistema OmniLibrary.
Utiliza Pydantic v2 para validação e serialização.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from enum import Enum


# Enums
class TipoAcervo(str, Enum):
    FISICO = "Físico"
    DIGITAL = "Digital"


class StatusEmprestimo(str, Enum):
    ATIVO = "Ativo"
    DEVOLVIDO = "Devolvido"
    ATRASADO = "Atrasado"


# Usuario
class UsuarioCreate(BaseModel):
    nome: str
    matricula: str
    is_bibliotecario: bool = False


class Usuario(UsuarioCreate):
    id: int

    class Config:
        from_attributes = True


# Obra
class ObraCreate(BaseModel):
    titulo: str
    tipo_acervo: TipoAcervo
    quantidade_disponivel: int
    eh_bestseller: bool = False

    @field_validator("quantidade_disponivel")
    @classmethod
    def quantidade_positiva(cls, v):
        if v < 0:
            raise ValueError("Quantidade disponível não pode ser negativa.")
        return v


class Obra(ObraCreate):
    id: int

    class Config:
        from_attributes = True


# Emprestimo
class EmprestimoCreate(BaseModel):
    usuario_id: int
    obra_id: int
    data_emprestimo: date
    data_vencimento: date


class Emprestimo(EmprestimoCreate):
    id: int
    data_devolucao: Optional[date] = None
    status: StatusEmprestimo = StatusEmprestimo.ATIVO

    class Config:
        from_attributes = True


# Reserva
class ReservaCreate(BaseModel):
    usuario_id: int
    obra_id: int


class Reserva(ReservaCreate):
    id: int
    data_solicitacao: date
    posicao_fila: int

    class Config:
        from_attributes = True


# Multa
class MultaCreate(BaseModel):
    emprestimo_id: int
    dias_atraso: int
    valor_total: float


class Multa(MultaCreate):
    id: int
    paga: bool = False

    class Config:
        from_attributes = True


# Schemas auxiliares de resposta
class AlertaVencimento(BaseModel):
    obra_titulo: str
    data_vencimento: date
    dias_restantes: int
    status: str  # "vencido" | "vence_hoje" | "vence_em_breve"
    mensagem: str