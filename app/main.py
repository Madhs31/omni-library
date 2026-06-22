from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Gestão de Biblioteca",
    description="API REST para controle de acervo, reservas, filas de prioridade e multas.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "Ok"}