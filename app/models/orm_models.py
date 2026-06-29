from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    matricula: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    is_bibliotecario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ObraORM(Base):
    __tablename__ = "obras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    tipo_acervo: Mapped[str] = mapped_column(String(30), nullable=False)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eh_bestseller: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EmprestimoORM(Base):
    __tablename__ = "emprestimos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"), nullable=False)
    data_emprestimo: Mapped[Date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[Date] = mapped_column(Date, nullable=False)
    data_devolucao: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Ativo", nullable=False)


class ReservaORM(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"), nullable=False)
    data_solicitacao: Mapped[Date] = mapped_column(Date, nullable=False)
    posicao_fila: Mapped[int] = mapped_column(Integer, nullable=False)


class MultaORM(Base):
    __tablename__ = "multas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emprestimo_id: Mapped[int] = mapped_column(ForeignKey("emprestimos.id"), nullable=False)
    dias_atraso: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    paga: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)