# Module 8 — CI/CD, Containerization & Deployment

## Mục tiêu module
Cung cấp hướng dẫn thực tế để đóng gói ứng dụng bằng Docker, tự động hoá build/test/publish bằng CI, và triển khai an toàn bằng Docker Compose hoặc Kubernetes. Sau module, bạn sẽ biết cách viết Dockerfile đúng chuẩn, tạo pipeline CI/CD (ví dụ GitHub Actions), chọn chiến lược triển khai, quản lý secrets và rollback khi cần.

## Lý thuyết
- Docker: đóng gói ứng dụng cùng runtime và dependencies để đảm bảo nhất quán giữa dev/staging/production.
- CI (Continuous Integration): tự động hóa build, lint, test mọi commit/PR.
- CD (Continuous Delivery/Deployment): tự động publish artifact (container image) và/hoặc tự động deploy lên môi trường.
- Registry: nơi lưu image (Docker Hub, GitHub Container Registry, AWS ECR, GCR).

## Giải thích chi tiết
1. Dockerfile multi-stage
- Mục tiêu: giảm kích thước image, tách build-time dependencies và artifacts runtime.
- Nguyên tắc: chỉ copy file cần thiết vào stage cuối cùng, dùng user không phải root, set HEALTHCHECK nếu cần.

Ví dụ Dockerfile multi-stage (Python FastAPI/Flask):

```dockerfile
# Stage 0: build deps (optional for compiled deps)
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml poetry.lock /app/
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Stage 1: runtime
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app
# an unprivileged user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Lưu ý: với pip/requirements.txt bạn có thể dùng pip wheel cache hoặc pip install --target.

2. Docker Compose cho dev
- Dùng docker-compose để compose app + DB + cache + worker cho dev.
- Giữ secrets qua `.env` hoặc `docker-compose.override.yml` (không commit .env mẫu chứa secrets thật).

Ví dụ `docker-compose.yml` tối giản:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - db-data:/var/lib/postgresql/data
volumes:
  db-data:
```

3. CI pipeline (GitHub Actions) — ví dụ
- Các stage thường thấy: lint -> test -> build image -> scan -> push image -> deploy.
- Sử dụng cache cho Docker layer và dependency cache để giảm thời gian build.

Ví dụ `.github/workflows/ci.yml` (mẫu):

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/poetry.lock') }}
      - name: Install deps
        run: |
          pip install poetry
          poetry install --no-dev
      - name: Lint
        run: poetry run flake8
      - name: Run tests
        run: poetry run pytest -q
      - name: Login to registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/trainingapi:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Gợi ý: tách job `test` và `build` thành hai job để tận dụng matrix/parallelism và tránh push image nếu test fail.

4. Image tagging & promotion
- Dùng `sha` cho traceability: `image:owner/repo:sha1`.
- Gắn thêm tag semver cho release: `:v1.2.3`.
- Promotion pattern: build image in CI -> push with `:sha` tag -> on release, tag image with `:vX.Y.Z` (or `latest` if appropriate).

5. Deployment strategies
- Rolling update: update dần các pods/instances, phổ biến và an toàn.
- Blue/Green: duy trì 2 môi trường (blue, green), chuyển traffic khi xanh OK.
- Canary: phóng thích cho % lưu lượng nhỏ trước khi mở rộng.

Ví dụ Kubernetes Deployment (simplified):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trainingapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trainingapi
  template:
    metadata:
      labels:
        app: trainingapi
    spec:
      containers:
        - name: web
          image: ghcr.io/OWNER/trainingapi:latest
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
```

6. Secrets management
- Dev: `.env` or Docker secrets for local; never commit secrets.
- Prod: use managed secrets (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager) hoặc Kubernetes Secrets with encryption at rest + RBAC.
- In CI: store secrets in CI provider secret store (GitHub Secrets) and avoid echoing them in logs.

7. Security & scanning
- Dependency scanning: Dependabot, Snyk, GitHub Dependabot alerts.
- Container scanning: trivy, clair, GitHub Container Scanning.
- IaC scanning: checkov, tfsec for Terraform resources.

8. Rollback
- Have a clear rollback plan: use Kubernetes rollout undo (`kubectl rollout undo deployment/trainingapi`) or redeploy previous image tag.
- Keep previous images in registry and implement health checks + automatic rollback if readiness not met.

## Checklist CI/CD (quick wins)
- [ ] Tests chạy trong pipeline và pass trước khi build image
- [ ] Multi-stage Dockerfile để tối ưu image size
- [ ] Build caching (actions cache hoặc buildkit cache) để giảm thời gian build
- [ ] Scan vulnerability dependencies & images
- [ ] Secrets lưu trong CI secret store / Vault
- [ ] Healthchecks (readiness/liveness) và resource requests/limits trong manifests
- [ ] Deployment strategy có rollback plan

## Bài tập thực hành
1) Viết `Dockerfile` multi-stage cho `TrainingAPI`, build và chạy local bằng Docker Compose.
2) Tạo workflow GitHub Actions để chạy lint + tests và build/push image lên GitHub Container Registry (ghcr.io). Sử dụng `GITHUB_TOKEN` để đăng nhập.
3) Viết manifest Kubernetes cho `TrainingAPI` kèm readiness/liveness probe; deploy lên k8s cluster (minikube/kind) và kiểm tra rolling update.
4) Thêm một bước scan image bằng `trivy` trong workflow; chặn push nếu phát hiện vulnerability nghiêm trọng.

## Tài nguyên & công cụ
- Dockerfile best practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- GitHub Actions: https://docs.github.com/actions
- Docker build-push-action: https://github.com/docker/build-push-action
- Trivy (container scanning): https://github.com/aquasecurity/trivy
- Helm charts & Kubernetes patterns: https://helm.sh/

---
