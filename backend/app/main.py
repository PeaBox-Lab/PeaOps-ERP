
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.core.db import Base, engine
from app.core.config import settings
from app.api.routes import router
from app.core.middleware import security_headers
from app.core.rate_limit import rate_limit
from app.security.middleware import authorization_policy
from app.core.runtime import validate_runtime
runtime_errors = validate_runtime(settings.environment, settings.database_url, settings.secret_key, settings.allowed_origins)
if runtime_errors:
    raise RuntimeError("; ".join(runtime_errors))
if settings.auto_create_schema:
    Base.metadata.create_all(bind=engine)
app = FastAPI(title="PeaOps ERP API", version="0.8.2")

@app.on_event("startup")
def startup_self_check():
    try:
        from app.core.db import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("Startup self-check: database OK")
    except Exception as exc:
        raise RuntimeError(f"Startup self-check failed: {exc}")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.allowed_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(security_headers)
app.middleware("http")(rate_limit)
app.middleware("http")(authorization_policy)
app.include_router(router)
_metrics = {"requests": 0, "errors": 0}

@app.middleware("http")
async def count_requests(request, call_next):
    _metrics["requests"] += 1
    response = await call_next(request)
    if response.status_code >= 500:
        _metrics["errors"] += 1
    return response

@app.get("/metrics")
def metrics():
    return _metrics

@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def metrics_prometheus():
    return (
        "# HELP peaops_requests_total Total HTTP requests served.\n"
        "# TYPE peaops_requests_total counter\n"
        f"peaops_requests_total {_metrics['requests']}\n"
        "# HELP peaops_errors_total Total HTTP 5xx responses.\n"
        "# TYPE peaops_errors_total counter\n"
        f"peaops_errors_total {_metrics['errors']}\n"
        "# HELP peaops_build_info PeaOps build information.\n"
        "# TYPE peaops_build_info gauge\n"
        'peaops_build_info{version="0.8.2"} 1\n'
    )

@app.get("/")
def root():
    return {"product": "PeaOps", "version": "0.8.2", "message": "Pilot hardening operating core", "docs": "/docs"}
