"""Send the digest via Gmail SMTP using an app password.

Credentials live in config/secrets.env (gitignored), KEY=VALUE per line:
    GMAIL_ADDR=you@gmail.com
    GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx     # 16-char Google app password
    GMAIL_TO=you@gmail.com                  # optional; defaults to GMAIL_ADDR
Environment variables of the same names override the file.
"""
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def secrets():
    env = {}
    sp = ROOT / "config" / "secrets.env"
    if sp.exists():
        for line in sp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    for k in ("GMAIL_ADDR", "GMAIL_APP_PASSWORD", "GMAIL_TO"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def send(to_addr, subject, body, pdf_path=None, html=None):
    s = secrets()
    addr, pw = s.get("GMAIL_ADDR"), s.get("GMAIL_APP_PASSWORD")
    if not addr or not pw:
        raise RuntimeError("Missing GMAIL_ADDR / GMAIL_APP_PASSWORD in config/secrets.env")
    msg = EmailMessage()
    msg["From"] = addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")
    if pdf_path and Path(pdf_path).exists():
        msg.add_attachment(Path(pdf_path).read_bytes(), maintype="application",
                           subtype="pdf", filename=Path(pdf_path).name)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as srv:
        srv.login(addr, pw)
        srv.send_message(msg)
    return True
