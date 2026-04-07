# Module 9 — Observability: Logging, Metrics, Tracing

## Lý thuyết
Observability gồm logging, metrics và tracing. Mục tiêu: hiểu trạng thái hệ thống và điều tra sự cố nhanh chóng.

## Giải thích
- Structured logging: logs dạng JSON có trường correlation_id giúp truy vết request.
- Metrics: latency, error rate, throughput; exposition cho Prometheus.
- Tracing: distributed tracing để theo dõi request xuyên nhiều service.

## Cách ứng dụng
1. Thêm structured logs (JSON) với correlation id middleware.
2. Expose metrics endpoint (`/metrics`) cho Prometheus.
3. Tích hợp OpenTelemetry SDK để emit traces, gửi đến Jaeger.

## Điểm cần lưu ý
- Không log sensitive data; thực hiện log sampling nếu high-volume.
- Định nghĩa SLO/SLI cơ bản để thiết lập alerting.

## Công nghệ liên quan
Prometheus, Grafana, OpenTelemetry, Jaeger, Loki, ELK stack
