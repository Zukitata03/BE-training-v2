# Module 10 — Advanced Topics & Patterns

## Lý thuyết
Các mẫu kiến trúc nâng cao: event-driven, CQRS, event sourcing, stream processing; trade-offs giữa GraphQL/REST/gRPC.

## Giải thích
- Event-driven: decoupling bằng message/event; phù hợp cho hệ phân tán và real-time.
- CQRS: tách đọc/ghi để tối ưu cho từng loại workload.
- Stream processing: xử lý dữ liệu liên tục (Kafka, KStreams).

## Cách ứng dụng
1. Thiết kế 1 use-case event-driven: khi user mượn sách -> emit event -> update lịch sử, gửi email.
2. Thực nghiệm CQRS cho endpoint read-heavy: tách read model lưu cache/denormalized data.
3. Xây dựng pipeline xử lý stream đơn giản với Kafka local.

## Điểm cần lưu ý
- Eventual consistency: hiểu trade-off và thiết kế user experience phù hợp.
- Sự phức tạp vận hành tăng khi dùng messaging/streaming.

## Công nghệ liên quan
Kafka, RabbitMQ, Debezium, Kafka Streams, GraphQL, Apache Flink
