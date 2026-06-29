from fastapi import FastAPI

from app.database import init_db
from app.controllers.livro_controller import (
    usuario_router,
    obra_router,
    emprestimo_router,
    reserva_router,
    multa_router,
)

app = FastAPI(
    title="OmniLibrary API",
    description=(
        "API REST para modernização do controle de acervos físicos e digitais.\n\n"
        "**Funcionalidades principais:**\n"
        "- RF01/RF02: Reserva antecipada com fila de prioridade para best-sellers\n"
        "- RF03: Cálculo automático de multas por atraso na devolução (R$ 2,50/dia)\n"
        "- RF04: Alertas inteligentes de vencimento de prazo\n"
        "- RF05: Gestão completa do acervo pelo bibliotecário\n"
        "- US03: Bloqueio de empréstimos para usuários com multas pendentes\n\n"
        "**Design Patterns:** Repository Pattern + Injeção de Dependência"
    ),
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(usuario_router)
app.include_router(obra_router)
app.include_router(emprestimo_router)
app.include_router(reserva_router)
app.include_router(multa_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "sistema": "OmniLibrary",
        "versao": "1.0.0",
        "docs": "/docs",
    }