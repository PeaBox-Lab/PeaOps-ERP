from urllib.parse import urlparse

def validate_runtime(environment:str,database_url:str,secret_key:str,allowed_origins:str):
    errors=[];env=environment.lower()
    if env in {'production','staging'}:
        if len(secret_key)<32 or secret_key in {'change-me','replace-this-before-production'}:errors.append('PEAOPS_SECRET_KEY must be a unique secret of at least 32 characters')
        if not database_url.startswith(('postgresql://','postgresql+psycopg://')):errors.append('Production and staging require PostgreSQL')
        origins=[x.strip() for x in allowed_origins.split(',') if x.strip()]
        if not origins or any(x=='*' or not x.startswith('https://') for x in origins):errors.append('Production allowed origins must be explicit HTTPS URLs')
    return errors
