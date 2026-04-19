from fastapi import FastAPI

app = FastAPI(
    title="Talent Interview Profile PoC",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
