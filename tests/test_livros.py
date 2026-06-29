import pytest
from datetime import date, timedelta

from app.repositories.livro_repository import (
    UsuarioRepository, ObraRepository,
    EmprestimoRepository, ReservaRepository, MultaRepository,
)
from app.services.livro_service import (
    UsuarioService, ObraService, EmprestimoService,
    ReservaService, MultaService, AlertaService,
    VALOR_MULTA_POR_DIA,
)


# Fixtures
@pytest.fixture
def db():
    """Banco isolado por teste — sem estado compartilhado entre casos."""
    counters = {"usuario": 0, "obra": 0, "emprestimo": 0, "reserva": 0, "multa": 0}

    def next_id(entity):
        counters[entity] += 1
        return counters[entity]

    return {
        "usuarios": {}, "obras": {}, "emprestimos": {},
        "reservas": {}, "multas": {}, "next_id": next_id,
    }


@pytest.fixture
def usuario_repo(db): return UsuarioRepository(db)
@pytest.fixture
def obra_repo(db): return ObraRepository(db)
@pytest.fixture
def emprestimo_repo(db): return EmprestimoRepository(db)
@pytest.fixture
def reserva_repo(db): return ReservaRepository(db)
@pytest.fixture
def multa_repo(db): return MultaRepository(db)

@pytest.fixture
def usuario_svc(usuario_repo): return UsuarioService(usuario_repo)
@pytest.fixture
def obra_svc(obra_repo): return ObraService(obra_repo)

@pytest.fixture
def emprestimo_svc(emprestimo_repo, obra_repo, usuario_repo, multa_repo, reserva_repo):
    return EmprestimoService(emprestimo_repo, obra_repo, usuario_repo, multa_repo, reserva_repo)

@pytest.fixture
def reserva_svc(reserva_repo, obra_repo, usuario_repo, multa_repo, emprestimo_repo):
    return ReservaService(reserva_repo, obra_repo, usuario_repo, multa_repo, emprestimo_repo)

@pytest.fixture
def multa_svc(multa_repo, emprestimo_repo, obra_repo):
    return MultaService(multa_repo, emprestimo_repo, obra_repo)

@pytest.fixture
def alerta_svc(emprestimo_repo, obra_repo):
    return AlertaService(emprestimo_repo, obra_repo)


# Helpers
def _usuario(repo, nome="Ana", matricula="MAT001", bibliotecario=False):
    return repo.criar({"nome": nome, "matricula": matricula, "is_bibliotecario": bibliotecario})

def _obra(repo, titulo="Python Fluente", qtd=2, bestseller=False):
    return repo.criar({
        "titulo": titulo, "tipo_acervo": "Físico",
        "quantidade_disponivel": qtd, "eh_bestseller": bestseller,
    })

def _emprestimo(repo, usuario_id=1, obra_id=1, dias_vencimento=14):
    hoje = date.today()
    return repo.criar({
        "usuario_id": usuario_id, "obra_id": obra_id,
        "data_emprestimo": hoje.isoformat(),
        "data_vencimento": (hoje + timedelta(days=dias_vencimento)).isoformat(),
    })


# Testes: UsuarioRepository
class TestUsuarioRepository:
    def test_criar_usuario(self, usuario_repo):
        u = _usuario(usuario_repo)
        assert u["id"] == 1 and u["nome"] == "Ana"

    def test_buscar_por_id(self, usuario_repo):
        u = _usuario(usuario_repo)
        assert usuario_repo.buscar_por_id(u["id"])["matricula"] == "MAT001"

    def test_buscar_por_matricula(self, usuario_repo):
        _usuario(usuario_repo)
        assert usuario_repo.buscar_por_matricula("MAT001") is not None

    def test_id_inexistente_retorna_none(self, usuario_repo):
        assert usuario_repo.buscar_por_id(99) is None

    def test_listar_todos(self, usuario_repo):
        _usuario(usuario_repo, "Ana", "MAT001")
        _usuario(usuario_repo, "Bob", "MAT002")
        assert len(usuario_repo.listar_todos()) == 2

    def test_deletar(self, usuario_repo):
        u = _usuario(usuario_repo)
        assert usuario_repo.deletar(u["id"]) is True
        assert usuario_repo.buscar_por_id(u["id"]) is None


# Testes: ObraRepository
class TestObraRepository:
    def test_criar_obra(self, obra_repo):
        o = _obra(obra_repo)
        assert o["id"] == 1 and o["quantidade_disponivel"] == 2

    def test_decrementar_quantidade(self, obra_repo):
        o = _obra(obra_repo, qtd=1)
        assert obra_repo.decrementar_quantidade(o["id"]) is True
        assert obra_repo.buscar_por_id(o["id"])["quantidade_disponivel"] == 0

    def test_nao_decrementa_quando_zero(self, obra_repo):
        o = _obra(obra_repo, qtd=0)
        assert obra_repo.decrementar_quantidade(o["id"]) is False

    def test_incrementar_quantidade(self, obra_repo):
        o = _obra(obra_repo, qtd=0)
        obra_repo.incrementar_quantidade(o["id"])
        assert obra_repo.buscar_por_id(o["id"])["quantidade_disponivel"] == 1

    def test_listar_disponiveis(self, obra_repo):
        _obra(obra_repo, "Livro A", qtd=2)
        _obra(obra_repo, "Livro B", qtd=0)
        disponiveis = obra_repo.listar_disponiveis()
        assert len(disponiveis) == 1 and disponiveis[0]["titulo"] == "Livro A"


# Testes: ReservaRepository
class TestReservaRepository:
    def test_fila_ordenada_por_posicao(self, reserva_repo):
        reserva_repo.criar({"usuario_id": 2, "obra_id": 1, "data_solicitacao": "2025-01-01", "posicao_fila": 2})
        reserva_repo.criar({"usuario_id": 1, "obra_id": 1, "data_solicitacao": "2025-01-01", "posicao_fila": 1})
        fila = reserva_repo.listar_fila_por_obra(1)
        assert fila[0]["posicao_fila"] == 1 and fila[1]["posicao_fila"] == 2

    def test_proxima_posicao_fila_vazia(self, reserva_repo):
        assert reserva_repo.proxima_posicao_na_fila(1) == 1

    def test_proxima_posicao_com_existentes(self, reserva_repo):
        reserva_repo.criar({"usuario_id": 1, "obra_id": 1, "data_solicitacao": "2025-01-01", "posicao_fila": 1})
        assert reserva_repo.proxima_posicao_na_fila(1) == 2

    def test_remover_primeiro_da_fila(self, reserva_repo):
        reserva_repo.criar({"usuario_id": 10, "obra_id": 1, "data_solicitacao": "2025-01-01", "posicao_fila": 1})
        reserva_repo.criar({"usuario_id": 20, "obra_id": 1, "data_solicitacao": "2025-01-01", "posicao_fila": 2})
        primeiro = reserva_repo.remover_primeiro_da_fila(1)
        assert primeiro["usuario_id"] == 10
        assert len(reserva_repo.listar_fila_por_obra(1)) == 1


# Testes: UsuarioService
class TestUsuarioService:
    def test_matricula_duplicada_levanta_erro(self, usuario_svc):
        usuario_svc.criar_usuario({"nome": "Ana", "matricula": "MAT001", "is_bibliotecario": False})
        with pytest.raises(ValueError, match="já cadastrada"):
            usuario_svc.criar_usuario({"nome": "Ana2", "matricula": "MAT001", "is_bibliotecario": False})

    def test_buscar_inexistente_levanta_erro(self, usuario_svc):
        with pytest.raises(ValueError, match="não encontrado"):
            usuario_svc.buscar_usuario(999)


# Testes: EmprestimoService
class TestEmprestimoService:
    def test_emprestimo_com_sucesso(self, emprestimo_svc, usuario_repo, obra_repo):
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=2)
        hoje = date.today()
        emp = emprestimo_svc.realizar_emprestimo({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=14)).isoformat(),
        })
        assert emp["id"] == 1
        assert obra_repo.buscar_por_id(1)["quantidade_disponivel"] == 1

    def test_emprestimo_sem_exemplar(self, emprestimo_svc, usuario_repo, obra_repo):
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=0)
        hoje = date.today()
        with pytest.raises(ValueError, match="sem exemplares disponíveis"):
            emprestimo_svc.realizar_emprestimo({
                "usuario_id": 1, "obra_id": 1,
                "data_emprestimo": hoje.isoformat(),
                "data_vencimento": (hoje + timedelta(days=14)).isoformat(),
            })

    def test_emprestimo_bloqueado_por_multa(
        self, emprestimo_svc, usuario_repo, obra_repo, emprestimo_repo, multa_repo
    ):
        """US03 — Bloquear empréstimo para usuário com multa ativa."""
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=3)
        hoje = date.today()
        emp = emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=20)).isoformat(),
            "data_vencimento": (hoje - timedelta(days=6)).isoformat(),
        })
        multa_repo.criar({"emprestimo_id": emp["id"], "dias_atraso": 6, "valor_total": 15.0})
        with pytest.raises(ValueError, match="multa"):
            emprestimo_svc.realizar_emprestimo({
                "usuario_id": 1, "obra_id": 1,
                "data_emprestimo": hoje.isoformat(),
                "data_vencimento": (hoje + timedelta(days=14)).isoformat(),
            })

    def test_devolucao_sem_atraso_sem_multa(
        self, emprestimo_svc, usuario_repo, obra_repo, emprestimo_repo
    ):
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=1)
        hoje = date.today()
        emp = emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=7)).isoformat(),
        })
        resultado = emprestimo_svc.registrar_devolucao(emp["id"])
        assert resultado["multa"] is None
        assert resultado["emprestimo"]["status"] == "Devolvido"

    def test_devolucao_com_atraso_gera_multa(
        self, emprestimo_svc, usuario_repo, obra_repo, emprestimo_repo
    ):
        """RF03 — Cálculo correto de multa por dias de atraso."""
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=1)
        hoje = date.today()
        emp = emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=20)).isoformat(),
            "data_vencimento": (hoje - timedelta(days=5)).isoformat(),
        })
        resultado = emprestimo_svc.registrar_devolucao(emp["id"])
        multa = resultado["multa"]
        assert multa is not None
        assert multa["dias_atraso"] == 5
        assert multa["valor_total"] == pytest.approx(5 * VALOR_MULTA_POR_DIA)

    def test_devolucao_dupla_levanta_erro(
        self, emprestimo_svc, usuario_repo, obra_repo, emprestimo_repo
    ):
        _usuario(usuario_repo)
        _obra(obra_repo, qtd=1)
        hoje = date.today()
        emp = emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=7)).isoformat(),
        })
        emprestimo_svc.registrar_devolucao(emp["id"])
        with pytest.raises(ValueError, match="já foi encerrado"):
            emprestimo_svc.registrar_devolucao(emp["id"])


# Testes: ReservaService 
class TestReservaService:
    def test_criar_reserva(self, reserva_svc, usuario_repo, obra_repo):
        """RF01 — Reserva antecipada com posição na fila."""
        _usuario(usuario_repo)
        _obra(obra_repo, bestseller=True)
        reserva = reserva_svc.criar_reserva(1, 1)
        assert reserva["posicao_fila"] == 1

    def test_fila_de_prioridade(self, reserva_svc, usuario_repo, obra_repo):
        """RF02 — Múltiplos usuários formam fila ordenada."""
        _usuario(usuario_repo, "Ana", "MAT001")
        _usuario(usuario_repo, "Bob", "MAT002")
        _usuario(usuario_repo, "Carol", "MAT003")
        _obra(obra_repo, bestseller=True)
        reserva_svc.criar_reserva(1, 1)
        reserva_svc.criar_reserva(2, 1)
        reserva_svc.criar_reserva(3, 1)
        fila = reserva_svc.visualizar_fila(1)
        assert [r["posicao_fila"] for r in fila] == [1, 2, 3]

    def test_reserva_duplicada(self, reserva_svc, usuario_repo, obra_repo):
        _usuario(usuario_repo)
        _obra(obra_repo)
        reserva_svc.criar_reserva(1, 1)
        with pytest.raises(ValueError, match="já possui reserva"):
            reserva_svc.criar_reserva(1, 1)

    def test_reserva_bloqueada_por_multa(
        self, reserva_svc, usuario_repo, obra_repo, emprestimo_repo, multa_repo
    ):
        _usuario(usuario_repo)
        _obra(obra_repo)
        hoje = date.today()
        emp = emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=20)).isoformat(),
            "data_vencimento": (hoje - timedelta(days=5)).isoformat(),
        })
        multa_repo.criar({"emprestimo_id": emp["id"], "dias_atraso": 5, "valor_total": 12.5})
        with pytest.raises(ValueError, match="multas pendentes"):
            reserva_svc.criar_reserva(1, 1)


# Testes: MultaService
class TestMultaService:
    def test_pagar_multa(self, multa_svc, multa_repo):
        m = multa_repo.criar({"emprestimo_id": 1, "dias_atraso": 3, "valor_total": 7.5})
        assert multa_svc.pagar_multa(m["id"])["paga"] is True

    def test_pagar_multa_ja_paga(self, multa_svc, multa_repo):
        m = multa_repo.criar({"emprestimo_id": 1, "dias_atraso": 3, "valor_total": 7.5})
        multa_svc.pagar_multa(m["id"])
        with pytest.raises(ValueError, match="já foi paga"):
            multa_svc.pagar_multa(m["id"])


# Testes: AlertaService
class TestAlertaService:
    def test_alerta_vence_hoje(self, alerta_svc, emprestimo_repo, obra_repo):
        """RF04 — Alerta quando a devolução é hoje."""
        _obra(obra_repo)
        hoje = date.today()
        emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=14)).isoformat(),
            "data_vencimento": hoje.isoformat(),
        })
        alertas = alerta_svc.alertas_usuario(1)
        assert any(a["status"] == "vence_hoje" for a in alertas)

    def test_alerta_vence_em_breve(self, alerta_svc, emprestimo_repo, obra_repo):
        _obra(obra_repo)
        hoje = date.today()
        emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=12)).isoformat(),
            "data_vencimento": (hoje + timedelta(days=2)).isoformat(),
        })
        alertas = alerta_svc.alertas_usuario(1)
        assert any(a["status"] == "vence_em_breve" for a in alertas)

    def test_alerta_vencido(self, alerta_svc, emprestimo_repo, obra_repo):
        _obra(obra_repo)
        hoje = date.today()
        emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": (hoje - timedelta(days=20)).isoformat(),
            "data_vencimento": (hoje - timedelta(days=3)).isoformat(),
        })
        alertas = alerta_svc.alertas_usuario(1)
        assert any(a["status"] == "vencido" for a in alertas)

    def test_sem_alertas_dentro_do_prazo(self, alerta_svc, emprestimo_repo, obra_repo):
        _obra(obra_repo)
        hoje = date.today()
        emprestimo_repo.criar({
            "usuario_id": 1, "obra_id": 1,
            "data_emprestimo": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=14)).isoformat(),
        })
        assert alerta_svc.alertas_usuario(1) == []