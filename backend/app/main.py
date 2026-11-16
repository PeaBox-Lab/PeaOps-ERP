from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import Base, engine
from app.api.routes import router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="PeaOps ERP API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.get("/")
def root():
    return {"product": "PeaOps", "version": "0.2.0", "message": "Finance operating core", "docs": "/docs"}
