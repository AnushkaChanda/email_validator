# Email Verification Engine (MVP)

A modular email verification pipeline designed following core industry standards (similar to NeverBounce and Reoon).

## 1. System Pipeline Architecture

[ Client (Flutter UI) ]
         │
         ▼ HTTP GET /validate?email=...
[ FastAPI Gateway ]
         │
  ┌──────┴────────────────────────────────────────┐
  │ 1. Syntax Check (RFC 5322 RegEx)              │
  │ 2. DNS Hostname Resolution (socket)           │
  │ 3. MX Record Check (DNS Resolver)             │
  │ 4. Disposable Domain Check (Blacklist Cache)   │
  │ 5. Role Account Detection (Prefix matching)   │
  │ 6. SMTP Simulation (HELO -> MAIL -> RCPT)     │
  └──────┬────────────────────────────────────────┘
         ▼
[ Scoring Engine ] ──► Log to SQLite Database (validations.db)
         │
         ▼
[ Structured JSON Response ]

## 2. Validation Stages

1. Syntax Check: Validates formatting via regex.
2. DNS & MX Check: Resolves domain existence and active mail exchangers.
3. Disposable Filter: Identifies temporary mail services.
4. Role Filter: Detects generic addresses (admin@, support@).
5. SMTP Verification: Tests mailbox deliverability via socket probe.

## 3. Real-World Limitations

- Cloud/ISP Port 25 Blocking: Outbound port 25 is blocked by default across consumer and cloud networks.
- Anti-Scraping Defenses: Major mail providers suppress RCPT verification to protect against harvesting.
- Scoring Resilience: Blocked/timed-out probes default to ACCEPT_ALL / UNKNOWN instead of false INVALID flags.
