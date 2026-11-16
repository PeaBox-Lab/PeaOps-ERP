from app.core.runtime import validate_runtime

def test_development_allows_sqlite():assert validate_runtime('development','sqlite:///./peaops.db','change-me','http://localhost:5173')==[]
def test_production_requires_strong_secret():assert any('SECRET_KEY' in x for x in validate_runtime('production','postgresql+psycopg://db','change-me','https://erp.example.com'))
def test_production_requires_postgres():assert any('PostgreSQL' in x for x in validate_runtime('production','sqlite:///db','x'*40,'https://erp.example.com'))
def test_production_requires_https_origin():assert any('HTTPS' in x for x in validate_runtime('production','postgresql+psycopg://db','x'*40,'http://erp.example.com'))
def test_valid_production_runtime():assert validate_runtime('production','postgresql+psycopg://db','x'*40,'https://erp.example.com')==[]
