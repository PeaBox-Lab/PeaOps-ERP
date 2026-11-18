import os, tempfile

_TMP = tempfile.mkdtemp(prefix="peaops-test-")
os.environ["PEAOPS_DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["PEAOPS_SECRET_KEY"] = "test-secret-key-that-is-long-enough-1234567890"
os.environ["PEAOPS_ENVIRONMENT"] = "development"
os.environ["PEAOPS_ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["PEAOPS_AUTO_CREATE_SCHEMA"] = "true"