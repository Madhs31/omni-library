# omni-library - Sistema de Gestão de Biblioteca

Este projeto consiste no desenvolvimento do back-end de uma API REST para modernizar o controle de acervos físicos e digitais de uma biblioteca. O sistema visa resolver problemas clássicos como o sumiço de obras, a falta de rotação adequada de best-sellers e a reeducação do leitor por meio de regras rigorosas de devolução, reservas e controle de multas.

## 👥 Integrantes 

- Angelina Borroni
- Maria Fernanda Diniz

---

## 🚀 Funcionalidades e Regras de Negócio

A API implementa os seguintes requisitos essenciais levantados na elicitação:

- **Reserva antecipada e fila de prioridade:** lógica otimizada para a reserva de exemplares altamente disputados, organizando os usuários em filas prioritárias.
- **Cálculo automatizado de multas:** sistema que calcula dinamicamente o valor das multas acumuladas por dia de atraso na devolução de obras.
- **Notificações inteligentes:** disparo de alertas automáticos e notificações sobre o vencimento próximo ou definitivo dos prazos de empréstimo.

---

## 📐 Arquitetura do Sistema e Design Patterns

O projeto foi construído utilizando **Python** e o framework **FastAPI**, estruturado seguindo o padrão de **Arquitetura em Camadas Limpas**, garantindo testabilidade, modularidade e facilidade de manutenção.

### Camadas da aplicação

- **Model:** contém a definição das entidades de dados e os esquemas de validação com Pydantic.
- **Repository:** camada responsável estritamente pelo acesso e persistência dos dados, isolando o banco de dados do restante da aplicação.
- **Service:** concentra todas as regras de negócio do sistema, como cálculo de multas, validação de prioridades e regras de devolução.
- **Controller:** define as rotas HTTP, lida com as requisições de entrada e envia as respostas apropriadas aos clientes.

### Padrões de Projeto (Design Patterns) Implementados

- **Repository Pattern:** utilizado para desacoplar a lógica de negócio da camada de acesso a dados, facilitando testes unitários e manutenção.
- **Arquitetura em Camadas:** separação clara entre responsabilidades de controle, serviço, persistência e modelagem.
- **Injeção de Dependência (quando aplicada no FastAPI):** facilita o desacoplamento entre componentes e melhora a testabilidade.

---

## 📂 Estrutura de Pastas

```text
OmniLibrary/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada e configuração da API FastAPI
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
│   └── models/                 # Camada de Entidades e Schemas
│       ├── __init__.py
│       └── livro_model.py
│
├── tests/                      # Testes automatizados da aplicação
│   ├── __init__.py
│   └── test_livros.py
│
├── .gitignore                  # Arquivo de descarte para arquivos locais e ambiente virtual
├── README.md                   # Documentação completa do projeto
└── requirements.txt            # Dependências e bibliotecas do projeto
````

---

## 🛠️ Instruções de Setup e Execução Local

### 1. Pré-requisitos

Antes de começar, você precisará ter instalado:

* **Python 3.10** ou superior
* **Git**

### 2. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/OmniLibrary.git
cd OmniLibrary
```

### 3. Configurar o ambiente virtual

Crie e ative o ambiente virtual do Python:

#### No Windows (PowerShell)

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### No Linux ou macOS

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar a aplicação

Inicie o servidor local em modo de desenvolvimento:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em:

```bash
http://127.0.0.1:8000
```

---

## 📖 Guia de Rotas e Documentação da API

Como o projeto utiliza **FastAPI**, a documentação interativa é gerada automaticamente.

### Documentações disponíveis

* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 🧪 Testes Automatizados

Os testes do sistema foram desenvolvidos utilizando **Pytest**, cobrindo cenários importantes das regras de negócio.

Para executar a suíte de testes, utilize o comando abaixo na raiz do projeto com o ambiente virtual ativo:

```bash
pytest
```
