"""Generate a self-signed cert for local pilot installs. Replace with a real cert in production."""
import datetime
import ipaddress
import sys
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization

site = sys.argv[1] if len(sys.argv) > 1 else "localhost"
import os
os.makedirs("certs", exist_ok=True)
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, site)])
now = datetime.datetime.now(datetime.timezone.utc)
alt = [x509.DNSName(site)] + ([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))] if site == "localhost" else [])
cert = (x509.CertificateBuilder()
        .subject_name(subject).issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now).not_valid_after(now + datetime.timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(alt), critical=False)
        .sign(key, hashes.SHA256()))
with open("certs/privkey.pem", "wb") as f:
    f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
with open("certs/fullchain.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print("certs written for", site)