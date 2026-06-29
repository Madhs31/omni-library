"""
Services — camada de regras de negócio do sistema OmniLibrary.

Cada serviço depende apenas dos repositórios (via injeção de dependência),
nunca acessa o banco diretamente — garantindo a separação de camadas.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.repositories.livro_repository import (
    UsuarioRepository, ObraRepository,
    EmprestimoRepository, ReservaRepository, MultaRepository,
)

# ─── Constantes de negócio ────────────────────────────────────────────────────

VALOR_MULTA_POR_DIA: float = 2.50       # R$ por dia de atraso (RF03)
DIAS_ALERTA_VENCIMENTO: int = 3         # Janela de alerta antes do vencimento (RF04)


# ─── Serviço de Usuários ──────────────────────────────────────────────────────

class UsuarioService:
    def __init__(self, repo: UsuarioRepository):
        self.repo = repo

    def criar_usuario(self, dados: dict) -> dict:
        if self.repo.buscar_por_matricula(dados["matricula"]):
            raise ValueError(f"Matrícula '{dados['matricula']}' já cadastrada.")
        return self.repo.criar(dados)

    def buscar_usuario(self, id: int) -> dict:
        usuario = self.repo.buscar_por_id(id)
        if not usuario:
            raise ValueError(f"Usuário {id} não encontrado.")
        return usuario

    def listar_usuarios(self) -> List[dict]:
        return self.repo.listar_todos()

    def deletar_usuario(self, id: int) -> bool:
        if not self.repo.buscar_por_id(id):
            raise ValueError(f"Usuário {id} não encontrado.")
        return self.repo.deletar(id)


# ─── Serviço de Obras ─────────────────────────────────────────────────────────

class ObraService:
    def __init__(self, repo: ObraRepository):
        self.repo = repo

    def cadastrar_obra(self, dados: dict) -> dict:
        return self.repo.criar(dados)

    def buscar_obra(self, id: int) -> dict:
        obra = self.repo.buscar_por_id(id)
        if not obra:
            raise ValueError(f"Obra {id} não encontrada.")
        return obra

    def listar_obras(self) -> List[dict]:
        return self.repo.listar_todos()

    def listar_disponiveis(self) -> List[dict]:
        return self.repo.listar_disponiveis()

    def listar_bestsellers(self) -> List[dict]:
        return self.repo.listar_bestsellers()

    def remover_obra(self, id: int) -> bool:
        if not self.repo.buscar_por_id(id):
            raise ValueError(f"Obra {id} não encontrada.")
        return self.repo.deletar(id)


# ─── Serviço de Empréstimos ───────────────────────────────────────────────────

class EmprestimoService:
    def __init__(
        self,
        emprestimo_repo: EmprestimoRepository,
        obra_repo: ObraRepository,
        usuario_repo: UsuarioRepository,
        multa_repo: MultaRepository,
        reserva_repo: ReservaRepository,
    ):
        self.emprestimo_repo = emprestimo_repo
        self.obra_repo = obra_repo
        self.usuario_repo = usuario_repo
        self.multa_repo = multa_repo
        self.reserva_repo = reserva_repo

    def _verificar_multas_pendentes(self, usuario_id: int):
        """
        US03: Bloqueia novos empréstimos se o usuário tiver multas ativas.
        Levanta ValueError com o total devido caso existam pendências.
        """
        emprestimos = self.emprestimo_repo.listar_por_usuario(usuario_id)
        pendentes = self.multa_repo.listar_pendentes_por_usuario(usuario_id, emprestimos)
        if pendentes:
            total = sum(m["valor_total"] for m in pendentes)
            raise ValueError(
                f"Usuário possui {len(pendentes)} multa(s) pendente(s) "
                f"totalizando R$ {total:.2f}. Quite as multas antes de novo empréstimo."
            )

    def realizar_emprestimo(self, dados: dict) -> dict:
        """RF01 (empréstimo) + US03 (bloqueio por multa)."""
        usuario_id = dados["usuario_id"]
        obra_id = dados["obra_id"]

        if not self.usuario_repo.buscar_por_id(usuario_id):
            raise ValueError(f"Usuário {usuario_id} não encontrado.")

        obra = self.obra_repo.buscar_por_id(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        # Bloquear por multa pendente (US03)
        self._verificar_multas_pendentes(usuario_id)

        if obra["quantidade_disponivel"] <= 0:
            raise ValueError(
                f"Obra '{obra['titulo']}' sem exemplares disponíveis. "
                "Use /reservas para entrar na fila de prioridade."
            )

        self.obra_repo.decrementar_quantidade(obra_id)
        return self.emprestimo_repo.criar(dados)

    def registrar_devolucao(self, emprestimo_id: int) -> dict:
        """
        RF03: Calcula e registra multa por atraso.
        RF02: Avança a fila de reservas ao devolver.
        Retorna: { emprestimo, multa | None, proximo_na_fila | None }
        """
        emprestimo = self.emprestimo_repo.buscar_por_id(emprestimo_id)
        if not emprestimo:
            raise ValueError(f"Empréstimo {emprestimo_id} não encontrado.")
        if emprestimo["status"] == "Devolvido":
            raise ValueError("Este empréstimo já foi encerrado.")

        hoje = date.today()
        vencimento = emprestimo["data_vencimento"]
        if isinstance(vencimento, str):
            vencimento = datetime.fromisoformat(vencimento).date()

        # Calcular multa se houver atraso
        dias_atraso = (hoje - vencimento).days
        multa = None
        if dias_atraso > 0:
            multa = self.multa_repo.criar({
                "emprestimo_id": emprestimo_id,
                "dias_atraso": dias_atraso,
                "valor_total": round(dias_atraso * VALOR_MULTA_POR_DIA, 2),
            })

        # Finalizar empréstimo
        self.emprestimo_repo.atualizar(emprestimo_id, {
            "data_devolucao": hoje.isoformat(),
            "status": "Devolvido",
        })

        # Devolver ao acervo e avançar fila (RF02)
        obra_id = emprestimo["obra_id"]
        proximo = self.reserva_repo.remover_primeiro_da_fila(obra_id)
        self.obra_repo.incrementar_quantidade(obra_id)

        return {
            "emprestimo": self.emprestimo_repo.buscar_por_id(emprestimo_id),
            "multa": multa,
            "proximo_na_fila": proximo,
        }

    def buscar_emprestimo(self, id: int) -> dict:
        emp = self.emprestimo_repo.buscar_por_id(id)
        if not emp:
            raise ValueError(f"Empréstimo {id} não encontrado.")
        return emp

    def listar_emprestimos_usuario(self, usuario_id: int) -> List[dict]:
        return self.emprestimo_repo.listar_por_usuario(usuario_id)


# ─── Serviço de Reservas ──────────────────────────────────────────────────────

class ReservaService:
    def __init__(
        self,
        reserva_repo: ReservaRepository,
        obra_repo: ObraRepository,
        usuario_repo: UsuarioRepository,
        multa_repo: MultaRepository,
        emprestimo_repo: EmprestimoRepository,
    ):
        self.reserva_repo = reserva_repo
        self.obra_repo = obra_repo
        self.usuario_repo = usuario_repo
        self.multa_repo = multa_repo
        self.emprestimo_repo = emprestimo_repo

    def criar_reserva(self, usuario_id: int, obra_id: int) -> dict:
        """RF01: Reserva antecipada. RF02: Posição na fila de prioridade."""
        if not self.usuario_repo.buscar_por_id(usuario_id):
            raise ValueError(f"Usuário {usuario_id} não encontrado.")
        if not self.obra_repo.buscar_por_id(obra_id):
            raise ValueError(f"Obra {obra_id} não encontrada.")

        # Bloquear por multa (consistência com US03)
        emprestimos = self.emprestimo_repo.listar_por_usuario(usuario_id)
        if self.multa_repo.listar_pendentes_por_usuario(usuario_id, emprestimos):
            raise ValueError("Usuário com multas pendentes não pode realizar reservas.")

        if self.reserva_repo.usuario_ja_reservou(usuario_id, obra_id):
            raise ValueError("Usuário já possui reserva para esta obra.")

        posicao = self.reserva_repo.proxima_posicao_na_fila(obra_id)
        return self.reserva_repo.criar({
            "usuario_id": usuario_id,
            "obra_id": obra_id,
            "data_solicitacao": date.today().isoformat(),
            "posicao_fila": posicao,
        })

    def visualizar_fila(self, obra_id: int) -> List[dict]:
        """RF02: Consulta a fila de prioridade de uma obra."""
        if not self.obra_repo.buscar_por_id(obra_id):
            raise ValueError(f"Obra {obra_id} não encontrada.")
        return self.reserva_repo.listar_fila_por_obra(obra_id)

    def cancelar_reserva(self, reserva_id: int, usuario_id: int) -> bool:
        reserva = self.reserva_repo.buscar_por_id(reserva_id)
        if not reserva:
            raise ValueError(f"Reserva {reserva_id} não encontrada.")
        if reserva["usuario_id"] != usuario_id:
            raise ValueError("Não autorizado: reserva pertence a outro usuário.")
        return self.reserva_repo.deletar(reserva_id)


# ─── Serviço de Multas ────────────────────────────────────────────────────────

class MultaService:
    def __init__(
        self,
        multa_repo: MultaRepository,
        emprestimo_repo: EmprestimoRepository,
        obra_repo: ObraRepository,
    ):
        self.multa_repo = multa_repo
        self.emprestimo_repo = emprestimo_repo
        self.obra_repo = obra_repo

    def pagar_multa(self, multa_id: int) -> dict:
        multa = self.multa_repo.buscar_por_id(multa_id)
        if not multa:
            raise ValueError(f"Multa {multa_id} não encontrada.")
        if multa["paga"]:
            raise ValueError("Esta multa já foi paga.")
        return self.multa_repo.atualizar(multa_id, {"paga": True})

    def listar_multas_usuario(self, usuario_id: int) -> List[dict]:
        emprestimos = self.emprestimo_repo.listar_por_usuario(usuario_id)
        ids = {e["id"] for e in emprestimos}
        return [m for m in self.multa_repo.listar_todos() if m["emprestimo_id"] in ids]

    def listar_todas(self) -> List[dict]:
        return self.multa_repo.listar_todos()


# ─── Serviço de Alertas ───────────────────────────────────────────────────────

class AlertaService:
    """
    RF04: Notificações de vencimento exibidas ao consultar o perfil do leitor.
    Classifica cada empréstimo ativo em: vencido | vence_hoje | vence_em_breve.
    """

    def __init__(self, emprestimo_repo: EmprestimoRepository, obra_repo: ObraRepository):
        self.emprestimo_repo = emprestimo_repo
        self.obra_repo = obra_repo

    def alertas_usuario(self, usuario_id: int) -> List[dict]:
        hoje = date.today()
        ativos = self.emprestimo_repo.listar_ativos_por_usuario(usuario_id)
        alertas = []

        for emp in ativos:
            vencimento = emp["data_vencimento"]
            if isinstance(vencimento, str):
                vencimento = datetime.fromisoformat(vencimento).date()

            dias = (vencimento - hoje).days
            obra = self.obra_repo.buscar_por_id(emp["obra_id"])
            titulo = obra["titulo"] if obra else f"Obra #{emp['obra_id']}"

            if dias < 0:
                alertas.append({
                    "obra_titulo": titulo,
                    "data_vencimento": vencimento.isoformat(),
                    "dias_restantes": abs(dias),
                    "status": "vencido",
                    "mensagem": f"⚠️ VENCIDO há {abs(dias)} dia(s). Devolva e quite a multa.",
                })
            elif dias == 0:
                alertas.append({
                    "obra_titulo": titulo,
                    "data_vencimento": vencimento.isoformat(),
                    "dias_restantes": 0,
                    "status": "vence_hoje",
                    "mensagem": "🔔 Devolução prevista para HOJE. Evite multas!",
                })
            elif dias <= DIAS_ALERTA_VENCIMENTO:
                alertas.append({
                    "obra_titulo": titulo,
                    "data_vencimento": vencimento.isoformat(),
                    "dias_restantes": dias,
                    "status": "vence_em_breve",
                    "mensagem": f"📅 Devolução em {dias} dia(s). Atenção ao prazo!",
                })

        return alertas