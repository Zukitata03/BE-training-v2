# Module 4 — Bảo mật ứng dụng (Security)

## Lý thuyết
Giới thiệu OWASP Top 10, nguyên tắc bảo mật thiết kế, và các kỹ thuật để giảm rủi ro (TLS, input validation, secrets management).

## Giải thích chi tiết
Dưới đây là các vấn đề bảo mật phổ biến theo OWASP Top 10 (tóm tắt) và cách phòng chống cơ bản:

1. Injection (SQL/NoSQL/Command injection)
   - Vấn đề: attacker chèn mã độc vào input để thao tác database hoặc hệ thống.
   - Phòng chống: dùng parameterized queries / prepared statements, ORM an toàn, validate/normalize input, tránh build query bằng string concat.

2. Broken Authentication
   - Vấn đề: xác thực yếu khiến attacker giả mạo user.
   - Phòng chống: password hashing (bcrypt/argon2), multi-factor auth khi cần, revoke/refresh token, session management an toàn.

3. Sensitive Data Exposure
   - Vấn đề: lộ PII hoặc secrets (config, keys, tokens).
   - Phòng chống: mã hoá dữ liệu at-rest khi cần, TLS cho data-in-transit, secret manager (Vault), không log thông tin nhạy cảm.

4. XML External Entities (XXE) / Insecure deserialization
   - Vấn đề: parse XML/serialized objects chứa payload gây hại.
   - Phòng chống: tắt XML external entities, dùng format an toàn (JSON/protobuf) hoặc validate strict schema.

5. Broken Access Control
   - Vấn đề: thiếu kiểm tra phân quyền, expose APIs cho user không có quyền.
   - Phòng chống: kiểm tra authorization server-side với RBAC/ABAC, avoid client-trusted authorization, enforce least privilege.

6. Security Misconfiguration
   - Vấn đề: cấu hình mặc định, debug mode, permissive CORS, verbose errors.
   - Phòng chống: harden config, disable debug in prod, cấu hình headers bảo mật, principle of least privilege.

7. Cross-Site Scripting (XSS)
   - Vấn đề: chèn mã JS vào trang, steal cookies/session.
   - Phòng chống: escape/encode output, Content Security Policy (CSP), sanitize input khi cần.

8. Insecure Deserialization
   - Vấn đề: deserialize dữ liệu không tin cậy dẫn đến RCE.
   - Phòng chống: tránh deserialize dữ liệu từ client, dùng safe serializers.

9. Using Components with Known Vulnerabilities
   - Vấn đề: dependency có lỗ hổng.
   - Phòng chống: dependency scanning (Snyk, Dependabot), cập nhật định kỳ, minimal dependencies.

10. Insufficient Logging & Monitoring
   - Vấn đề: không phát hiện được hành vi tấn công kịp thời.
   - Phòng chống: structured logging, alerting, central log aggregation, không log secrets.

## Cách ứng dụng — Cấu hình và ví dụ thực tế

1) HTTPS / TLS
- Luôn dùng HTTPS trong production. Local dev có thể dùng self-signed certs.
- Sử dụng HSTS header để ép trình duyệt chỉ kết nối qua HTTPS.
- Quản lý chứng chỉ với Let's Encrypt + certbot hoặc vault/managed cert in cloud.

Ví dụ tạo self-signed cert (local):

```bash
# Tạo self-signed cert (dev only)
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
```

2) Secure headers (ví dụ với Sanic)

- Content-Security-Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy
- Strict-Transport-Security (HSTS)

Ví dụ (Sanic middleware):

```text
from sanic import Sanic
from sanic.response import json
app = Sanic("training_api")

@app.middleware('response')
async def set_secure_headers(request, response):
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return

# Sample route
@app.route('/')
async def index(request):
    return json({'ok': True})
```

3) Input validation & output encoding
- Validate shape/constraints using JSON Schema / pydantic / marshmallow.
- Sanitize HTML inputs or store as plain text and escape on render.

Ví dụ (pydantic request validation in FastAPI):

```text
from pydantic import BaseModel
class BookCreate(BaseModel):
    title: str
    author_id: str
    pages: int
```

4) Parameterized queries (Ngăn injection)

- PostgreSQL (psycopg2) example:

```text
# Good: parameterized
cur.execute("SELECT * FROM books WHERE title = %s", (title,))
```

- MongoDB (pymongo): tránh build filter với string concat; pass dicts

```text
books = db.books.find({"title": title})
```

5) Passwords & tokens
- Hash password với bcrypt/argon2; lưu hashed + salt.
- Access token ngắn hạn; refresh token lưu an toàn (DB hoặc httpOnly cookie).
- Thiết kế cơ chế thu hồi token (blacklist hoặc token versioning per user).

6) Rate limiting & brute-force protection
- Áp dụng rate limiting theo IP/endpoint, dùng tools: Flask-Limiter, nginx rate limit.

Ví dụ Sanic-Limiter:

```text
from sanic import Sanic
from sanic.response import json
from sanic_limiter import Limiter
from sanic_limiter.util import get_remote_address

app = Sanic("training_api")
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

@app.route('/login')
@limiter.limit('5 per minute')
async def login(request):
    return json({'ok': True})
```

7) CSRF protection
- Với cookie-based auth, bảo vệ CSRF bằng token (csrf-token) hoặc SameSite=strict/ lax.
- Frameworks: Flask-WTF, Django built-in CSRF middleware.

8) Secrets management & rotation
- Không commit secrets. Dùng environment variables cho dev, Vault (HashiCorp) cho prod.
- Thiết kế rotation policy: rotate keys/credentials định kỳ.

Ví dụ pattern: lưu DB password trong Vault; app lúc runtime lấy temporary credential.

9) Dependency scanning & SCA
- Tích hợp Snyk, Dependabot hoặc GitHub Actions để quét dependency vulnerabilities.
- Có policy để chấp nhận/upgrade hoặc block PR nếu vuln nghiêm trọng.

10) Logging & incident response
- Structured logs (JSON), include correlation_id, log levels.
- Không log PII; mask hoặc redact sensitive fields.
- Thiết lập alerting cho error rate spike, auth failures, high latency.

## Checklist bảo mật (quick wins)
- [ ] Bật HTTPS cho production
- [ ] Disable debug mode & verbose errors
- [ ] Thiết lập secure headers (CSP, HSTS, X-Frame-Options)
- [ ] Hash và salt passwords (bcrypt/argon2)
- [ ] Dùng parameterized queries, ORM an toàn
- [ ] Thêm rate limiting cho các endpoint nhạy cảm
- [ ] Tích hợp dependency scanning
- [ ] Thiết lập centralized logging và alerting
- [ ] Quản lý secrets không lưu trong repo

## Bài tập thực hành (kịch bản)
1. Hardening API: bật HTTPS (local bằng self-signed), thêm secure headers và rate limit cho `/login`.
2. Viết unit/integration test để chứng minh injection không thể xảy ra: thử gửi payload có pattern injection và assert hệ thống không thực thi.
3. Tạo flow refresh token + blacklist khi user đổi mật khẩu; kiểm tra token cũ không còn tác dụng.
4. Thiết lập Dependabot hoặc Snyk scan cho repo và fix một vulnerability nhỏ.

## Công nghệ liên quan (chi tiết hơn)
- Secrets: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
- TLS/Certs: Let's Encrypt + Certbot, ACME client
- Rate limiting: Flask-Limiter, nginx rate limiting, Cloudflare
- Input validation: pydantic, marshmallow, cerberus
- Dependency scanning: Snyk, Dependabot, GitHub Advanced Security
- Scanners & SAST: Bandit (Python), Semgrep

## Tài nguyên tham khảo
- OWASP Top Ten: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- HashiCorp Vault docs: https://www.vaultproject.io/
- Let's Encrypt / Certbot docs: https://letsencrypt.org/

---