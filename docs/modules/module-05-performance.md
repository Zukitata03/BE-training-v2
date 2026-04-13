# Module 5 — Hiệu năng & Tối ưu

## Lý thuyết (mở rộng)
Các nguyên tắc tối ưu: đo lường trước khi tối ưu, xác định cổ chai, ưu tiên tối ưu chi phí-hiệu quả. Các khái niệm quan trọng:
- Độ trễ (latency) vs Lưu lượng (throughput) vs Đồng thời (concurrency)
- Điểm nghẽn (bottleneck): CPU, Memory, I/O (disk/DB/network)
- P50/P95/P99 latency: đo phân vị để biết trải nghiệm người dùng
- Các đánh đổi: nhất quán (consistency) vs độ trễ, tính tươi mới dữ liệu (freshness) vs tỉ lệ trúng cache (cache hit-rate)

## Phân tích hiệu năng & Chẩn đoán
Mục tiêu: biết đo ở đâu (ứng dụng, cơ sở dữ liệu, hạ tầng) và dùng công cụ phù hợp.

1) CPU profiling
- Instrumentation (cProfile): thu thập chi tiết callstack nhưng có overhead.
- Sampling (py-spy, perf): ít overhead, phù hợp để chẩn đoán trên production.

Ví dụ chạy py-spy (sampling) để tạo flame graph:

```text
# Cài py-spy và chụp profile 30s
py-spy record -o profile.svg --pid <PID> --duration 30
# Mở profile.svg để xem flamegraph
```

2) Phân tích bộ nhớ
- Tracemalloc (builtin Python) để theo dõi phân bổ object.
- Heapy / guppy để phân tích heap; objgraph để tìm memory leak.

3) I/O và cơ sở dữ liệu
- Dùng EXPLAIN/EXPLAIN ANALYZE cho SQL; dùng công cụ tương ứng cho MongoDB (mongotop, explain) để phân tích.
- Theo dõi hàng đợi kết nối (connection queueing), contention trên lock.

4) Tracing end-to-end
- OpenTelemetry + Jaeger để trace request đi xuyên nhiều service, giúp xác định phần nào tốn thời gian nhất.

## Chiến lược caching (chi tiết)
Caching là công cụ mạnh nhưng dễ sai. Các pattern chính:

1) Cache-aside (tải khi cần — lazy loading)
- Ứng dụng đọc cache; nếu miss thì đọc DB rồi ghi cache.
- Ưu: đơn giản. Nhược: cache stale, thundering herd.

2) Write-through
- Ghi vào cache đồng thời với DB (đồng bộ) hoặc trước khi ghi DB.
- Ưu: cache luôn nhất quán; Nhược: tăng độ trễ ghi.

3) Write-back (write-behind)
- Ghi vào cache, flush vào DB bất kỳ lúc nào (bất đồng bộ).
- Ưu: giảm độ trễ ghi; Nhược: rủi ro mất dữ liệu khi crash.

4) Read-Through (middleware)
- Lớp cache tự động fetch từ DB khi miss (ví dụ caching proxy).

5) HTTP Caching
- Sử dụng Cache-Control, ETag, Last-Modified, Vary headers.
- Dùng CDN cho static assets và các response API có thể cache.

Thiết kế key cho cache
- Key = namespace + resource + version + params
- Tránh cardinality không giới hạn (không dùng query string nguyên bản làm key)
- Thêm TTL và tags (nếu cần) để invalidation theo nhóm

Các cách invalidation cache
- TTL theo thời gian
- Invalidation dựa trên sự kiện (emit event khi update -> invalidate các key liên quan)
- Versioning (đổi prefix version cho key) — đơn giản và đáng tin cậy
- stale-while-revalidate: trả giá trị cũ trong khi refresh bất đồng bộ

Giảm thundering herd
- Dùng request coalescing / lock (mutex per key) để chỉ có 1 request thực hiện refill cache
- Thêm jitter cho TTL để tránh hết hạn cùng lúc

## Connection pooling & tuning tài nguyên
- Kích thước pool kết nối DB/Redis cần phù hợp với concurrency mong đợi và khả năng DB.
- Công thức tham khảo: max_pool = (worker_processes * threads_per_worker) * concurrent_requests_per_worker / estimated_db_concurrency_factor
- Với framework async, dùng driver async có pooling (aiopg, asyncpg, motor)
- Theo dõi thời gian chờ pool; nếu lâu nghĩa là pool đang bị thiếu

## Async vs Sync, mô hình đồng thời
- Sync (WSGI) với nhiều tiến trình worker (Gunicorn): đơn giản, phù hợp workload ít I/O.
- Async (asyncio, Sanic/FastAPI + Uvicorn/Hypercorn): tốt cho I/O-bound với nhiều kết nối đồng thời.
- Multiprocessing cho tác vụ CPU-bound (hoặc offload sang job queue)

## Background jobs & gom nhóm (batching)
- Offload tác vụ nặng hoặc không cần đồng bộ sang worker (Celery/RQ/Dramatiq).
- Gom nhóm các thao tác nhỏ để giảm overhead (bulk insert/update thay vì nhiều ghi đơn lẻ).

Ví dụ task Celery (giữ nguyên mã):

```text
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def send_email_batch(emails):
    for e in emails:
        send_email(e)
```

## Mạng, nén, HTTP/2, CDN
- Bật gzip / brotli cho responses; nén các payload lớn.
- Dùng HTTP/2 để multiplex nhiều request trên cùng 1 TCP.
- Dùng CDN để cache và phân phối static asset và các API có thể cache đến gần người dùng.
- Keepalive giảm overhead thiết lập kết nối.

## Tối ưu ở tầng cơ sở dữ liệu
- Index: tạo index cho các truy vấn thường xuyên; cân nhắc partial và covering index.
- Denormalize cho pattern read-heavy; materialized views cho các phép toán tổng hợp tốn kém.
- Dùng kiểu dữ liệu phù hợp và tránh SELECT *.
- Chiến lược phân trang: offset-based (đơn giản) vs cursor-based (tốt khi scale lớn)

## Quan sát hiệu năng (Observability)
- Thu thập metrics: requests/sec, error rate, p50/p95/p99 latency, thời gian query DB, cache hit rate, độ dài hàng đợi.
- Dùng dashboard (Grafana) và cảnh báo khi SLO bị vi phạm (ví dụ p95 > ngưỡng) hoặc dấu hiệu saturation.

## Load & Stress Testing — ví dụ bằng Python (Locust)
Dưới là ví dụ sử dụng Locust để mô phỏng load test cho endpoint `/api/books`. Locust là công cụ load-testing viết bằng Python, dễ mở rộng bằng code Python.

Tạo file `locustfile.py` với nội dung sau:

```text
from locust import HttpUser, task, between

class BooksUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def list_books(self):
        self.client.get('/api/books')

    @task(2)
    def get_book(self):
        # giả sử có book id 1 cho mục đích test
        self.client.get('/api/books/1')
```

Chạy Locust ở chế độ headless (không GUI) để chạy load test tự động:

```bash
# cài locust nếu chưa có
pip install locust
# chạy headless: -u = total users, -r = spawn rate users/sec, --run-time = thời gian chạy
locust -f locustfile.py --headless -u 200 -r 50 --run-time 2m --host https://localhost:8443
```

Kết quả sẽ in ra throughput, latency trung bình và phân vị p95/p99 trên terminal; bạn cũng có thể chạy Locust với GUI (không dùng --headless) và mở http://localhost:8089 để điều khiển thử nghiệm.

(Đổi `self.client.get` path nếu API của bạn khác; với HTTPS tự-signed trong môi trường dev, có thể cần thêm cấu hình để bỏ qua xác thực chứng chỉ hoặc dùng `--host` trỏ tới endpoint hợp lệ.)

## Đo lường lặp lại & tính khả tái lặp
- Tự động hóa test (CI) cho performance nếu khả thi (smoke load tests trên staging)
- Chụp baseline metrics trước khi thay đổi
- Dùng môi trường có kiểm soát để giảm tiếng ồn (cùng cấu hình máy, warm caches)

## Giải thích metrics: p50/p95/p99
- p50: độ trễ trung vị (trải nghiệm điển hình)
- p95/p99: độ trễ ở đuôi (ảnh hưởng nhỏ hơn nhưng quan trọng với UX)
- Tập trung giảm tail latency để cải thiện trải nghiệm người dùng

## Ví dụ: thêm cache cho endpoint (khái niệm)
Các bước:
1) Xác định endpoint nặng/chậm qua profiling hoặc metric
2) Thiết kế key cache và TTL
3) Triển khai cache-aside: check cache -> nếu miss đọc DB -> set cache
4) Giám sát cache hit rate và tác động lên DB

Pseudo-code (text):

```text
# cache-aside
key = f"books:page:{page}:q:{query_hash}:v1"
val = redis.get(key)
if val:
    return val
else:
    val = db.query(...)  # expensive
    redis.set(key, serialize(val), ex=60)
    return val
```

## Checklist tối ưu hiệu năng
- [ ] Thu thập baseline metrics (latency, throughput)
- [ ] Profile app để xác định hotspot (CPU/memory/DB)
- [ ] Thêm cache cho các endpoint phù hợp; đo cache hit rate
- [ ] Tối ưu queries & thêm index nếu cần
- [ ] Tune DB connection pool sizing
- [ ] Offload heavy tasks vào background job
- [ ] Thực hiện load test & phân tích p95/p99
- [ ] Thiết lập dashboard metrics và alerts cho SLOs

## Bài tập thực hành (đề xuất)
1) Profile và tối ưu: dùng `py-spy` để thu CPU profile khi chạy `TrainingAPI`, xác định 1 hàm chậm và tối ưu (hoặc memoize)
2) Caching: implement cache-aside cho endpoint list `GET /books`, so sánh latency và DB RPS trước/sau
3) Load test: chạy k6 script ở trên trên staging; capture p50/p95/p99; tối ưu (thêm cache, tăng pool) và re-run
4) Background jobs: tách thao tác gửi email/thumbnails generation sang Celery worker; đo giảm latency request

---

Nếu bạn muốn, tôi có thể:
- Tạo một ví dụ runnable trong `examples/perf-sample/` (Sanic app + Redis + Celery + k6 script) để bạn chạy local bằng `docker-compose`.
- Hoặc chỉ tạo k6/locust scripts và ví dụ code cụ thể trên `TrainingAPI` để bạn áp dụng.
Hãy cho tôi biết bước tiếp theo bạn muốn (ví dụ: tạo `examples/perf-sample/` hay thêm cache vào `TrainingAPI`).
