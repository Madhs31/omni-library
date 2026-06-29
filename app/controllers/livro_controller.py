from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.livro_model import (
    UsuarioCreate, ObraCreate,
    EmprestimoCreate, ReservaCreate,
)
from app.services.livro_service import (
    UsuarioService, ObraService, EmprestimoService,
    ReservaService, MultaService, AlertaService,
)
from app.database import get_db
from app.repositories.livro_repository import (
    UsuarioRepository, ObraRepository,
    EmprestimoRepository, ReservaRepository, MultaRepository,
)


def get_usuario_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


def get_obra_service(db: Session = Depends(get_db)) -> ObraService:
    return ObraService(ObraRepository(db))


def get_emprestimo_service(db: Session = Depends(get_db)) -> EmprestimoService:
    return EmprestimoService(
        EmprestimoRepository(db),
        ObraRepository(db),
        UsuarioRepository(db),
        MultaRepository(db),
        ReservaRepository(db),
    )


def get_reserva_service(db: Session = Depends(get_db)) -> ReservaService:
    return ReservaService(
        ReservaRepository(db),
        ObraRepository(db),
        UsuarioRepository(db),
        MultaRepository(db),
        EmprestimoRepository(db),
    )


def get_multa_service(db: Session = Depends(get_db)) -> MultaService:
    return MultaService(
        MultaRepository(db),
        EmprestimoRepository(db),
        ObraRepository(db),
    )


def get_alerta_service(db: Session = Depends(get_db)) -> AlertaService:
    return AlertaService(EmprestimoRepository(db), ObraRepository(db))

# Router de Usuários
usuario_router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@usuario_router.post("/", status_code=201)
def criar_usuario(dados: UsuarioCreate, svc: UsuarioService = Depends(get_usuario_service)):
    try:
        return svc.criar_usuario(dados.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@usuario_router.get("/")
def listar_usuarios(svc: UsuarioService = Depends(get_usuario_service)):
    return svc.listar_usuarios()

@usuario_router.get("/{usuario_id}")
def buscar_usuario(usuario_id: int, svc: UsuarioService = Depends(get_usuario_service)):
    try:
        return svc.buscar_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@usuario_router.delete("/{usuario_id}", status_code=204)
def deletar_usuario(usuario_id: int, svc: UsuarioService = Depends(get_usuario_service)):
    try:
        svc.deletar_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@usuario_router.get("/{usuario_id}/alertas")
def alertas_usuario(
    usuario_id: int,
    alerta_svc: AlertaService = Depends(get_alerta_service),
    usuario_svc: UsuarioService = Depends(get_usuario_service),
):
    """RF04 — Exibe alertas de vencimento ao consultar o perfil do leitor."""
    try:
        usuario_svc.buscar_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return alerta_svc.alertas_usuario(usuario_id)


# Router de Obras
obra_router = APIRouter(prefix="/obras", tags=["Obras"])

@obra_router.post("/", status_code=201)
def cadastrar_obra(dados: ObraCreate, svc: ObraService = Depends(get_obra_service)):
    return svc.cadastrar_obra(dados.model_dump())

@obra_router.get("/")
def listar_obras(svc: ObraService = Depends(get_obra_service)):
    return svc.listar_obras()

@obra_router.get("/disponiveis")
def listar_disponiveis(svc: ObraService = Depends(get_obra_service)):
    return svc.listar_disponiveis()

@obra_router.get("/bestsellers")
def listar_bestsellers(svc: ObraService = Depends(get_obra_service)):
    return svc.listar_bestsellers()

@obra_router.get("/{obra_id}")
def buscar_obra(obra_id: int, svc: ObraService = Depends(get_obra_service)):
    try:
        return svc.buscar_obra(obra_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@obra_router.delete("/{obra_id}", status_code=204)
def remover_obra(obra_id: int, svc: ObraService = Depends(get_obra_service)):
    try:
        svc.remover_obra(obra_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Router de Empréstimos
emprestimo_router = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])

@emprestimo_router.post("/", status_code=201)
def realizar_emprestimo(dados: EmprestimoCreate, svc: EmprestimoService = Depends(get_emprestimo_service)):
    try:
        return svc.realizar_emprestimo(dados.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@emprestimo_router.post("/{emprestimo_id}/devolucao")
def registrar_devolucao(emprestimo_id: int, svc: EmprestimoService = Depends(get_emprestimo_service)):
    """RF03 — Registra devolução e calcula multa automática por atraso."""
    try:
        return svc.registrar_devolucao(emprestimo_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@emprestimo_router.get("/usuario/{usuario_id}")
def emprestimos_por_usuario(usuario_id: int, svc: EmprestimoService = Depends(get_emprestimo_service)):
    return svc.listar_emprestimos_usuario(usuario_id)

@emprestimo_router.get("/{emprestimo_id}")
def buscar_emprestimo(emprestimo_id: int, svc: EmprestimoService = Depends(get_emprestimo_service)):
    try:
        return svc.buscar_emprestimo(emprestimo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Router de Reservas
reserva_router = APIRouter(prefix="/reservas", tags=["Reservas"])

@reserva_router.post("/", status_code=201)
def criar_reserva(dados: ReservaCreate, svc: ReservaService = Depends(get_reserva_service)):
    """RF01 + RF02 — Reserva antecipada com entrada automática na fila de prioridade."""
    try:
        return svc.criar_reserva(dados.usuario_id, dados.obra_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@reserva_router.get("/fila/{obra_id}")
def fila_de_reservas(obra_id: int, svc: ReservaService = Depends(get_reserva_service)):
    """RF02 — Visualiza a fila de prioridade de uma obra."""
    try:
        return svc.visualizar_fila(obra_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@reserva_router.delete("/{reserva_id}/usuario/{usuario_id}", status_code=204)
def cancelar_reserva(
    reserva_id: int,
    usuario_id: int,
    svc: ReservaService = Depends(get_reserva_service),
):
    try:
        svc.cancelar_reserva(reserva_id, usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Router de Multas
multa_router = APIRouter(prefix="/multas", tags=["Multas"])

@multa_router.get("/")
def listar_multas(svc: MultaService = Depends(get_multa_service)):
    return svc.listar_todas()

@multa_router.get("/usuario/{usuario_id}")
def multas_por_usuario(usuario_id: int, svc: MultaService = Depends(get_multa_service)):
    return svc.listar_multas_usuario(usuario_id)

@multa_router.patch("/{multa_id}/pagar")
def pagar_multa(multa_id: int, svc: MultaService = Depends(get_multa_service)):
    try:
        return svc.pagar_multa(multa_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))