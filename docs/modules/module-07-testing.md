# Module 7 — Testing & Quality Assurance

## Lý thuyết
Các loại test: unit, integration, end-to-end, contract; test pyramid; test doubles và test isolation.

## Giải thích
- Unit test: kiểm tra logic nhỏ, nhanh, không phụ thuộc external.
- Integration test: kiểm tra tương tác với DB hoặc external services (dùng test DB hoặc containerized DB).
- Contract test: đảm bảo compatibility giữa consumer và provider.

## Cách ứng dụng
1. Viết unit tests cho service/utility functions (pytest).
2. Thiết lập integration tests dùng pytest + testcontainers hoặc sqlite/memory DB.
3. Thêm test coverage và chạy trong CI pipeline.

## Điểm cần lưu ý
- Tránh test brittle (dễ vỡ khi thay đổi implementation).
- Dùng fixtures để tái sử dụng setup/teardown.

## Công nghệ liên quan
pytest, unittest, testcontainers, Faker, factory_boy, coverage, pact-python
