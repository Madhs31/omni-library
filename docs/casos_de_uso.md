# Diagrama de Casos de Uso

```mermaid
flowchart LR
    %% Atores
    Leitor((Leitor))
    Bibliotecario((Bibliotecário))

    %% Sistema
    subgraph CLI ["CLI - Gestão de Biblioteca"]
        direction TB
        UC1([Executar Comando de Pesquisa])
        UC2([Executar Comando de Reserva])
        UC3([Consultar Status e Multas])
        UC4([Cadastrar Nova Obra])
        UC5([Registrar Empréstimo])
        UC6([Registrar Devolução - Calcula Multa/Fila])
    end

    %% Relacionamentos do Leitor
    Leitor --> UC1
    Leitor --> UC2
    Leitor --> UC3

    %% Relacionamentos do Bibliotecário
    Bibliotecario --> UC1
    Bibliotecario --> UC3
    Bibliotecario --> UC4
    Bibliotecario --> UC5
    Bibliotecario --> UC6
```