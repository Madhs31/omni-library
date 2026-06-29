# 📚 OmniLibrary — Sistema de Gestão de Biblioteca

API REST desenvolvida em **Python + FastAPI** para modernizar o controle de acervos físicos e digitais de uma biblioteca, com reservas antecipadas, fila de prioridade, cálculo automático de multas e alertas de vencimento.

---

## 👥 Integrantes

- Angelina Borroni
- Maria Fernanda Diniz

---

## 🚀 Funcionalidades e Regras de Negócio

| Requisito | Descrição |
|------------|-----------|
| **RF01 — Reserva Antecipada** | Usuários podem reservar obras antes de elas ficarem disponíveis, garantindo posição na fila. |
| **RF02 — Fila de Prioridade** | Na devolução de um exemplar, o próximo usuário da fila é identificado automaticamente. |
| **RF03 — Multas Automáticas** | Cálculo automático de **R$ 2,50 por dia de atraso** na devolução. |
| **RF04 — Alertas de Vencimento** | Alertas para empréstimos vencidos ou próximos do vencimento. |
| **RF05 — Gestão do Acervo** | Cadastro, listagem, busca e remoção de obras do acervo. |
| **US03 — Bloqueio por Multa** | Usuários com multas pendentes não podem realizar novos empréstimos ou reservas. |

---

## 🧱 Tecnologias Utilizadas

- **Linguagem:** Python
- **Framework REST:** FastAPI
- **Validação de dados:** Pydantic
- **Banco de dados:** SQLite
- **ORM:** SQLAlchemy
- **Design Pattern:** Repository Pattern
- **Testes:** Pytest

---

# 📐 Arquitetura do Sistema

O projeto segue uma arquitetura em camadas, separando responsabilidades entre rotas, regras de negócio, persistência e modelos de dados.

```txt
Cliente HTTP
    │
    ▼
Controllers
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
SQLite + SQLAlchemy
```

### Camadas da aplicação

- **Controllers:** definem as rotas HTTP da API.
- **Services:** concentram as regras de negócio, como cálculo de multa, validação de reservas e bloqueio por multa.
- **Repositories:** fazem o acesso ao banco de dados usando SQLAlchemy.
- **Models:** armazenam os schemas Pydantic e os modelos ORM.
- **Database:** configura a conexão com o SQLite.

---

# 🧩 Design Patterns

## Repository Pattern

O projeto utiliza o Repository Pattern para separar a lógica de negócio da lógica de acesso ao banco de dados. Dessa forma, os serviços não acessam diretamente o SQLite, mas sim os repositórios.

## Dependency Injection

O FastAPI utiliza `Depends()` para injetar dependências, como a sessão do banco e os serviços usados pelas rotas.

## Layered Architecture

A aplicação é dividida em camadas, facilitando manutenção, testes e evolução do projeto.

---

# 🗂️ Estrutura de Pastas

```txt
OmniLibrary/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da API FastAPI
│   ├── database.py             # Reexporta configurações do banco
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # Conexão SQLite, SessionLocal, Base e init_db
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── livro_controller.py # Rotas da API
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── livro_service.py    # Regras de negócio
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── livro_repository.py # Acesso ao banco de dados
│   │
│   └── models/
│       ├── __init__.py
│       ├── livro_model.py      # Schemas Pydantic
│       └── orm_models.py       # Modelos SQLAlchemy
│
├── docs/
│   ├── casos_de_uso.puml
│   └── classes.puml
│
├── tests/
│   ├── __init__.py
│   └── test_livros.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 🗃️ Banco de Dados

O projeto utiliza **SQLite** no desenvolvimento local. O banco é criado automaticamente ao iniciar a aplicação.

### Arquivo gerado localmente

```text
omnilibrary.db
```

Esse arquivo não deve ser enviado para o GitHub, por isso deve estar listado no `.gitignore`.

### Tabelas principais

#### usuarios

```text
id
nome
matricula
is_bibliotecario
```

#### obras

```text
id
titulo
tipo_acervo
quantidade_disponivel
eh_bestseller
```

#### emprestimos

```text
id
usuario_id
obra_id
data_emprestimo
data_vencimento
data_devolucao
status
```

#### reservas

```text
id
usuario_id
obra_id
data_solicitacao
posicao_fila
```

#### multas

```text
id
emprestimo_id
dias_atraso
valor_total
paga
```

---

# 🛠️ Como Executar o Projeto

## Pré-requisitos

- Python 3.10 ou superior
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/Madhs31/omni-library.git
cd omni-library
```

### 2. Criar e ativar o ambiente virtual

**Windows**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS**

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

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

---

# 📖 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

# 🔗 Endpoints Disponíveis

## Usuários — `/usuarios`

| Método | Rota | Descrição |
|---------|------|-----------|
| POST | `/usuarios` | Cria um usuário. |
| GET | `/usuarios` | Lista todos os usuários. |
| GET | `/usuarios/{usuario_id}` | Busca usuário por ID. |
| DELETE | `/usuarios/{usuario_id}` | Remove usuário. |
| GET | `/usuarios/{usuario_id}/alertas` | Lista alertas de vencimento do usuário. |

---

## Obras — `/obras`

| Método | Rota | Descrição |
|---------|------|-----------|
| POST | `/obras` | Cadastra uma obra. |
| GET | `/obras` | Lista todas as obras. |
| GET | `/obras/disponiveis` | Lista obras disponíveis. |
| GET | `/obras/bestsellers` | Lista obras best-sellers. |
| GET | `/obras/{obra_id}` | Busca obra por ID. |
| DELETE | `/obras/{obra_id}` | Remove obra. |

---

## Empréstimos — `/emprestimos`

| Método | Rota | Descrição |
|---------|------|-----------|
| POST | `/emprestimos` | Realiza empréstimo. |
| POST | `/emprestimos/{emprestimo_id}/devolucao` | Registra devolução e calcula multa, se houver atraso. |
| GET | `/emprestimos/usuario/{usuario_id}` | Lista empréstimos de um usuário. |
| GET | `/emprestimos/{emprestimo_id}` | Busca empréstimo por ID. |

---

## Reservas — `/reservas`

| Método | Rota | Descrição |
|---------|------|-----------|
| POST | `/reservas` | Cria uma reserva e posiciona o usuário na fila. |
| GET | `/reservas/fila/{obra_id}` | Visualiza a fila de reservas de uma obra. |
| DELETE | `/reservas/{reserva_id}/usuario/{usuario_id}` | Cancela uma reserva. |

---

## Multas — `/multas`

| Método | Rota | Descrição |
|---------|------|-----------|
| GET | `/multas` | Lista todas as multas. |
| GET | `/multas/usuario/{usuario_id}` | Lista multas de um usuário. |
| PATCH | `/multas/{multa_id}/pagar` | Registra pagamento de multa. |

---

# 🧪 Testes Automatizados

Os testes foram desenvolvidos com **Pytest**.

### Executar todos os testes

```bash
pytest
```

### Executar em modo detalhado

```bash
pytest -v
```
