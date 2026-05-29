from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import query, schema

app = FastAPI(title="NEXUS - Engineering War Room")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(schema.router, prefix="/api", tags=["Schema"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
