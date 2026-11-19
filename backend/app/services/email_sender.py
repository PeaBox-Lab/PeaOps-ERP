"""Generic document email sender using SMTP (env or saved smtp_settings table)."""
import smtplib
import ssl
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64

def resolve_smtp(db):
    """Returns (host, port, username, password, from_address, use_tls) or (None,) if not configured."""
    from app.core.config import settings
    env = settings.smtp_host
    if env:
        return (env, settings.smtp_port, settings.smtp_username, settings.smtp_password, settings.smtp_from or settings.smtp_username, settings.smtp_tls)
    from app.domain.models import SmtpSetting
    from sqlalchemy import select
    obj = db.scalar(select(SmtpSetting))
    if obj and obj.host and obj.active:
        return (obj.host, obj.port, obj.username, obj.password, obj.from_address or obj.username, obj.use_tls)
    return (None,)

def build_multipart(company_name, doc_number, document_type, to_email, subject, body_text, pdf_bytes, filename):
    msg = MIMEMultipart()
    msg['From'] = f"{company_name} <noreply@peaops.local>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)
    return msg

def send_email(db, company_name, doc_number, document_type, to_email, subject, body_text, pdf_bytes, filename):
    host, port, username, password, from_addr, use_tls = resolve_smtp(db)
    if host is None:
        link = f"mailto:{to_email}?subject={subject}&body={body_text}"
        return {"sent": False, "reason": "smtp_not_configured", "mailto": link, "to": to_email, "subject": subject}
    msg = MIMEMultipart()
    msg['From'] = from_addr or "peaops@localhost"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)
    try:
        context = ssl.create_default_context() if use_tls else None
        with smtplib.SMTP(host, port, context=context) as server:
            if username:
                server.login(username, password)
            server.sendmail(msg['From'], [to_email], msg.as_string())
    except Exception as exc:
        raise RuntimeError(f"SMTP send failed: {exc}")
    return {"sent": True, "to": to_email, "subject": subject}