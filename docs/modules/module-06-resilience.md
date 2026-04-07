# Module 6 — Độ tin cậy & Resilience

## Lý thuyết
Các patterns để tăng độ bền hệ thống: retry với exponential backoff, circuit breaker, bulkhead, graceful shutdown, health checks.

## Giải thích
- Circuit breaker: ngăn cascade failures khi một service phụ trợ bị lỗi.
- Bulkhead: cô lập tài nguyên để tránh lỗi lan rộng.
- Graceful shutdown: cho phép hoàn thành request hiện tại và đóng kết nối an toàn khi service dừng.

## Cách ứng dụng
1. Cài đặt health endpoints (/health/live, /health/ready) cho orchestration.
2. Sử dụng thư viện circuit breaker hoặc trung gian (e.g., Envoy) cho service-to-service calls.
3. Bắt SIGTERM/SIGINT và thực hiện shutdown sequence (stop accepting new requests, drain connections, finish jobs).

## Điểm cần lưu ý
- Health check phải đơn giản và nhanh; readiness check có thể kiểm tra DB/Redis kết nối.
- Retry nên đi kèm với idempotency để tránh duplicate effects.

## Công nghệ liên quan
Hystrix (concept), resilience4j, envoy, Kubernetes readiness/liveness, systemd
