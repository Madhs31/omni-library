# 📚 OmniLibrary — Sistema de Gestão de Biblioteca

> API REST desenvolvida em **Python + FastAPI** para modernizar o controle de acervos físicos e digitais de uma biblioteca, com reservas antecipadas, fila de prioridade, cálculo automático de multas e alertas inteligentes de vencimento.

---

## 👥 Integrantes

- **Angelina Borroni**
- **Maria Fernanda Diniz**

---

## 🚀 Funcionalidades e Regras de Negócio

A API implementa os seguintes requisitos levantados na elicitação do **Grupo 5 — Gestão de Biblioteca**:

| Requisito | Descrição |
|-----------|-----------|
| **RF01 — Reserva Antecipada** | Usuários podem reservar obras antes de elas ficarem disponíveis, garantindo posição na fila. |
| **RF02 — Fila de Prioridade** | Na devolução de um exemplar, o próximo da fila é automaticamente notificado. |
| **RF03 — Multas Automáticas** | Cálculo automático de **R$ 2,50 por dia de atraso** na devolução. |
| **RF04 — Alertas de Vencimento** | Notificações inteligentes para empréstimos vencidos ou próximos do vencimento. |
| **US03 — Bloqueio por Multa** | Usuários com multas pendentes são bloqueados de realizar novos empréstimos ou reservas. |

---

## 📐 Arquitetura do Sistema e Design Patterns

O projeto foi construído com **Python** e **FastAPI**, seguindo o padrão de **Arquitetura em Camadas Limpas**, garantindo testabilidade, modularidade e facilidade de manutenção.

### Camadas da aplicação

```
Cliente HTTP (Swagger UI / curl / app)
       |
  [ Controller ]     livro_controller.py
  Rotas HTTP — valida entrada, retorna response
       | Depends()
  [ Service ]        livro_service.py
  Regras de negócio — multas, filas, alertas, bloqueios
       |
  [ Repository ]     livro_repository.py
  Acesso a dados — CRUD e consultas por entidade
       |
  [ Database ]       database.py
  Banco em memória — dicionários Python + IDs sequenciais
       |
  [ Model ]          livro_model.py
  Schemas Pydantic v2 — validação de tipos + Enums
```

### Design Patterns implementados

**1. Repository Pattern** *(padrão principal)*

Uma classe abstrata `BaseRepository` define o contrato (interface); cinco repositórios concretos implementam o acesso a dados para cada entidade. Isso isola completamente a lógica de negócio do banco de dados — para trocar o banco em memória por PostgreSQL, basta criar uma nova implementação concreta sem alterar nenhum serviço.

**2. Dependency Injection** *(via FastAPI `Depends()`)*

Cada serviço recebe seus repositórios por injeção de dependência, garantindo instâncias frescas por request e facilitando a substituição por mocks nos testes.

**3. Layered Architecture**

Cada camada só conhece a imediatamente abaixo dela. O Controller nunca acessa o banco diretamente; o Repository nunca contém regras de negócio.

---

## 🗂️ Diagramas UML

Os diagramas estão na pasta `docs/` em formato PlantUML:

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `docs/casos_de_uso.puml` | Casos de Uso | Atores (Leitor e Bibliotecário) e suas interações com o sistema |
| `docs/classes.puml` | Diagrama de Classes | Entidades do domínio (Usuario, Obra, Emprestimo, Reserva, Multa) e relacionamentos |

Para visualizar, importe os arquivos em [https://www.plantuml.com/plantuml](https://www.plantuml.com/plantuml) ou use a extensão PlantUML no VS Code.

---

## 📂 Estrutura de Pastas

```
OmniLibrary/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada e configuração da API FastAPI
│   ├── database.py             # Banco de dados em memória
│   │
│   ├── controllers/            # Camada de Rotas / Endpoints HTTP
│   │   ├── __init__.py
│   │   └── livro_controller.py
│   │
│   ├── services/               # Camada de Regras de Negócio
│   │   ├── __init__.py
│   │   └── livro_service.py
│   │
│   ├── repositories/           # Camada de Persistência / Acesso a Dados
│   │   ├── __init__.py
│   │   └── livro_repository.py
│   │
│   └── models/                 # Camada de Entidades e Schemas Pydantic
│       ├── __init__.py
│       └── livro_model.py
│
├── tests/                      # Testes automatizados com Pytest
│   ├── __init__.py
│   └── test_livros.py
│
├── docs/                       # Diagramas UML em PlantUML
│   ├── casos_de_uso.puml
│   └── classes.puml
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🛠️ Instruções de Setup e Execução Local

### Pré-requisitos

- **Python 3.10** ou superior
- **Git**

### 1. Clonar o repositório

```bash
git clone https://github.com/Madhs31/omni-library.git
cd omni-library
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://127.0.0.1:8000`

---

## 📖 Guia de Rotas da API

A documentação interativa completa está disponível após subir o servidor:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### Endpoints disponíveis

#### 👤 Usuários — `/usuarios`

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `POST` | `/usuarios` | 201 / 400 | Cria novo usuário. Erro 400 se matrícula já existe. |
| `GET` | `/usuarios` | 200 | Lista todos os usuários. |
| `GET` | `/usuarios/{id}` | 200 / 404 | Busca usuário por ID. |
| `DELETE` | `/usuarios/{id}` | 204 / 404 | Remove usuário. |
| `GET` | `/usuarios/{id}/alertas` | 200 / 404 | **RF04:** Retorna alertas de vencimento do usuário. |

#### 📕 Obras — `/obras`

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `POST` | `/obras` | 201 | Cadastra nova obra no acervo. |
| `GET` | `/obras` | 200 | Lista todas as obras. |
| `GET` | `/obras/disponiveis` | 200 | Lista obras com exemplares disponíveis. |
| `GET` | `/obras/bestsellers` | 200 | Lista obras marcadas como best-seller. |
| `GET` | `/obras/{id}` | 200 / 404 | Busca obra por ID. |
| `DELETE` | `/obras/{id}` | 204 / 404 | Remove obra do acervo. |

#### 🔄 Empréstimos — `/emprestimos`

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `POST` | `/emprestimos` | 201 / 400 | **RF01 + US03:** Realiza empréstimo. Bloqueia se houver multa pendente ou sem estoque. |
| `POST` | `/emprestimos/{id}/devolucao` | 200 / 400 | **RF02 + RF03:** Registra devolução, calcula multa automática e avança fila. |
| `GET` | `/emprestimos/usuario/{id}` | 200 | Lista todos os empréstimos de um usuário. |
| `GET` | `/emprestimos/{id}` | 200 / 404 | Busca empréstimo por ID. |

#### 📋 Reservas — `/reservas`

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `POST` | `/reservas` | 201 / 400 | **RF01 + RF02:** Cria reserva e posiciona usuário na fila de prioridade. |
| `GET` | `/reservas/fila/{obra_id}` | 200 / 404 | **RF02:** Visualiza fila de prioridade de uma obra. |
| `DELETE` | `/reservas/{id}/usuario/{uid}` | 204 / 400 | Cancela reserva (valida que pertence ao usuário). |

#### 💰 Multas — `/multas`

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| `GET` | `/multas` | 200 | Lista todas as multas do sistema. |
| `GET` | `/multas/usuario/{id}` | 200 | Lista multas de um usuário (pagas e pendentes). |
| `PATCH` | `/multas/{id}/pagar` | 200 / 400 | **RF03:** Registra pagamento de uma multa. |

---

## 🧪 Testes Automatizados

Os testes foram desenvolvidos com **Pytest**, usando banco de dados isolado por teste (fixture) para garantir independência entre os casos.

### Executar os testes

```bash
pytest           # rodar todos os testes
pytest -v        # modo verboso (nome de cada teste)
```

### Cobertura da suíte

| Classe de teste | O que cobre |
|----------------|-------------|
| `TestUsuarioRepository` | CRUD, busca por matrícula, IDs inexistentes. |
| `TestObraRepository` | Criação, decremento/incremento de estoque, filtros. |
| `TestEmprestimoRepository` | Criação, filtragem por usuário, listagem de ativos. |
| `TestReservaRepository` | Fila de reservas, posicionamento, duplicatas. |
| `TestMultaRepository` | Criação de multas, listagem de pendentes por usuário. |
| `TestUsuarioService` | Matrícula duplicada, busca de usuário inexistente. |
| `TestObraService` | Cadastro, busca e remoção de obras. |
| `TestEmprestimoService` | Empréstimo normal, bloqueio **US03**, cálculo **RF03**, devolução dupla. |
| `TestReservaService` | Reserva **RF01**, fila **RF02**, bloqueio por multa, duplicata. |
| `TestMultaService` | Pagamento de multa, erro em multa já paga. |
| `TestAlertaService` | Alertas vencido / vence_hoje / vence_em_breve / nenhum — **RF04**. |
