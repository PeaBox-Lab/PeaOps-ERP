from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import Base, engine
from app.core.config import settings
from app.api.routes import router
from app.core.middleware import security_headers
from app.core.runtime import validate_runtime
runtime_errors = validate_runtime(settings.environment, settings.database_url, settings.secret_key, settings.allowed_origins)
if runtime_errors:
    raise RuntimeError("; ".join(runtime_errors))
if settings.auto_create_schema:
    Base.metadata.create_all(bind=engine)
app = FastAPI(title="PeaOps ERP API", version="0.8.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.allowed_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(security_headers)
app.include_router(router)
@app.get("/")
def root():
    return {"product": "PeaOps", "version": "0.8.0", "message": "Production foundation operating core", "docs": "/docs"}
