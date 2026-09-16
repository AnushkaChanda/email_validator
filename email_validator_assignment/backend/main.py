import re
import socket
import smtplib
import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import dns.resolver
from database import init_db, log_validation, DB_NAME

app = FastAPI(title="Email Validator Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

with open("disposable_domains.json", "r") as f:
    DISPOSABLE_DOMAINS = set(json.load(f))

ROLE_PREFIXES = {
    "admin", "info", "support", "sales", "help", 
    "contact", "billing", "jobs", "careers", "security"
}

def check_syntax(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def check_domain_dns(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False

def get_mx_record(domain: str):
    try:
        records = dns.resolver.resolve(domain, "MX")
        sorted_records = sorted(records, key=lambda r: r.preference)
        return str(sorted_records[0].exchange).rstrip(".")
    except Exception:
        return None

def verify_smtp(mx_host: str, recipient_email: str) -> str:
    try:
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_host, 25)
        server.helo("validator.local")
        server.mail("check@validator.local")
        code, _ = server.rcpt(recipient_email)
        server.quit()
        
        if code == 250:
            return "deliverable"
        elif code in (550, 551, 552, 553):
            return "undeliverable"
        else:
            return "blocked_or_unknown"
    except Exception:
        return "blocked_or_unknown"

# --- ADDED ROOT ROUTE ---
@app.get("/")
def read_root():
    return {
        "service": "Email Quality Inspector API",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": ["/validate", "/history"]
    }

@app.get("/validate")
def validate_email(email: str = Query(..., example="alex@company.com")):
    email = email.strip().lower()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    if not check_syntax(email):
        res = {
            "email": email,
            "syntax": "invalid",
            "domain_exists": False,
            "mx_found": False,
            "disposable": False,
            "role_account": False,
            "smtp": "untested",
            "status": "INVALID",
            "timestamp": timestamp
        }
        log_validation(email, res["status"], json.dumps(res))
        return res

    local_part, domain = email.split("@", 1)
    domain_ok = check_domain_dns(domain)
    mx_host = get_mx_record(domain) if domain_ok else None

    if not domain_ok or not mx_host:
        res = {
            "email": email,
            "syntax": "valid",
            "domain_exists": domain_ok,
            "mx_found": bool(mx_host),
            "disposable": False,
            "role_account": False,
            "smtp": "unreachable",
            "status": "INVALID",
            "timestamp": timestamp
        }
        log_validation(email, res["status"], json.dumps(res))
        return res

    is_disposable = domain in DISPOSABLE_DOMAINS
    is_role = local_part in ROLE_PREFIXES
    smtp_status = verify_smtp(mx_host, email)

    if is_disposable:
        status = "RISKY (Disposable)"
    elif is_role:
        status = "RISKY (Role Account)"
    elif smtp_status == "deliverable":
        status = "VALID"
    elif smtp_status == "undeliverable":
        status = "INVALID"
    else:
        status = "ACCEPT_ALL / UNKNOWN"

    result = {
        "email": email,
        "syntax": "valid",
        "domain_exists": True,
        "mx_found": True,
        "disposable": is_disposable,
        "role_account": is_role,
        "smtp": smtp_status,
        "status": status,
        "timestamp": timestamp
    }
    
    log_validation(email, result["status"], json.dumps(result))
    return result

@app.get("/history")
def get_recent_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, status, checked_at FROM validation_logs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "email": r[1], "status": r[2], "checked_at": r[3]} for r in rows]