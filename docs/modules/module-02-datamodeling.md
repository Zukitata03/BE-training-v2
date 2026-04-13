# Module 2 — Cơ sở dữ liệu & Data Modeling

# 1. Kiến thức nền tảng về Database

## 1.1. Database là gì

Database là hệ thống dùng để **lưu trữ, quản lý và truy xuất dữ liệu** một cách có tổ chức.  
Trong backend, database là nơi lưu toàn bộ trạng thái của hệ thống: user, transaction, log, cấu hình…

Backend không lưu dữ liệu trực tiếp mà luôn thông qua database.

---

## 1.2. Vai trò của Database trong hệ thống

- Lưu trữ dữ liệu lâu dài (persistent storage)
- Đảm bảo tính toàn vẹn và nhất quán của dữ liệu
- Cho phép truy vấn và cập nhật dữ liệu hiệu quả
- Là nguồn dữ liệu duy nhất (source of truth) của hệ thống

→ Backend đọc/ghi dữ liệu thông qua database để xử lý nghiệp vụ

---

## 1.3. Phân loại Database

### Relational Database (RDBMS)

- Dữ liệu tổ chức theo **bảng (table)**
- Có schema rõ ràng
- Sử dụng SQL

**Đặc điểm:**
- Có quan hệ giữa các bảng (foreign key)
- Tuân thủ ACID
- Phù hợp dữ liệu có cấu trúc chặt chẽ

**Ví dụ:**
- PostgreSQL
- MySQL

---

### NoSQL Database

- Không bắt buộc schema cố định
- Linh hoạt về cấu trúc dữ liệu

**Các loại chính:**
- Key-value (Redis)
- Document (MongoDB)
- Column-family (Cassandra)

**Đặc điểm:**
- Scale tốt
- Linh hoạt
- Thường không mạnh về join như SQL

---

## 1.4. Row-based vs Column-based

### Row-based (OLTP)

- Lưu dữ liệu theo từng dòng
- Tối ưu cho:
  - Insert / Update / Delete
  - Query theo record

**Ví dụ:**
- PostgreSQL, MySQL

---

### Column-based (OLAP)

- Lưu dữ liệu theo cột
- Tối ưu cho:
  - Analytics
  - Aggregation (SUM, COUNT…)

**Ví dụ:**
- ClickHouse, BigQuery

---

## 1.5. OLTP vs OLAP

### OLTP (Online Transaction Processing)

- Xử lý giao dịch hàng ngày
- Nhiều read/write nhỏ
- Yêu cầu consistency cao

**Ví dụ:**
- Hệ thống user, order, payment

---

### OLAP (Online Analytical Processing)

- Phân tích dữ liệu
- Query lớn, scan nhiều data
- Ít write, nhiều read

**Ví dụ:**
- Dashboard, báo cáo, BI

---

## 1.6. Khi nào dùng loại nào

- **RDBMS (PostgreSQL, MySQL):**
  - Dữ liệu có cấu trúc rõ
  - Quan hệ phức tạp
  - Cần transaction

- **NoSQL:**
  - Dữ liệu linh hoạt
  - Scale lớn
  - Không cần join phức tạp

- **Column DB (OLAP):**
  - Analytics, reporting
  - Query aggregation lớn

---

## Tổng kết

- Database là trung tâm lưu trữ dữ liệu của backend
- Có 2 hướng chính: SQL (structured) và NoSQL (flexible)
- Phân biệt rõ OLTP vs OLAP để chọn đúng loại database
- Hiểu bản chất lưu trữ (row vs column) để tối ưu hệ thống

# Index trong Database

## 1. Khái niệm
Index là Là cấu trúc dữ liệu đặc biệt giúp tăng tốc độ truy xuất thông tin trong bảng (table) mà không cần quét toàn bộ dữ liệu.

---

## 2. Bản chất
- Mapping: value → vị trí dữ liệu
- Giảm từ **O(n) → O(log n)** (B-Tree)

---

## 3. Các loại chính
- Single index: 1 cột
- Composite index: nhiều cột (có thứ tự)
- Unique index: không cho phép trùng
- Primary key: tự động có index

---

## 4. Khi nên dùng index

Nên tạo index cho các cột thường xuyên xuất hiện trong các câu truy vấn, đặc biệt là trong mệnh đề WHERE, JOIN và ORDER BY, vì đây là những nơi database cần tìm kiếm và sắp xếp dữ liệu. Index giúp giảm đáng kể thời gian xử lý trong các trường hợp này.

Ngoài ra, index phát huy hiệu quả tốt nhất với các cột có **độ phân biệt cao (high cardinality)**, tức là có nhiều giá trị khác nhau (ví dụ: email, user_id). Khi đó, index giúp thu hẹp phạm vi tìm kiếm rất nhanh.

---

## 5. Khi không nên dùng index

Không nên sử dụng index cho các bảng nhỏ, vì việc scan toàn bộ bảng đôi khi nhanh hơn việc sử dụng index.

Các cột có ít giá trị lặp lại (low cardinality) như boolean, giới tính, trạng thái... cũng không phù hợp để đánh index, vì index không giúp giảm nhiều phạm vi tìm kiếm.

Ngoài ra, trong các hệ thống có tần suất ghi cao (INSERT, UPDATE, DELETE), việc sử dụng quá nhiều index sẽ làm giảm hiệu năng, do mỗi lần ghi dữ liệu database phải cập nhật thêm các index liên quan.

## 6. Trade-off

Việc sử dụng index giúp tăng tốc đáng kể các truy vấn đọc (SELECT), đặc biệt với dữ liệu lớn. Tuy nhiên, đổi lại, hiệu năng ghi sẽ bị ảnh hưởng vì mỗi lần INSERT, UPDATE hoặc DELETE, database phải cập nhật cả dữ liệu và các index liên quan.

Ngoài ra, index cũng tiêu tốn thêm dung lượng lưu trữ, đặc biệt khi bảng có nhiều index hoặc dữ liệu lớn.

---

## 7. Lưu ý quan trọng

Khi sử dụng composite index (index nhiều cột), thứ tự các cột là rất quan trọng vì database chỉ có thể tận dụng index theo nguyên tắc "left-most prefix".

Không nên tạo index một cách tùy tiện (over-indexing), vì sẽ làm giảm hiệu năng ghi và tăng chi phí hệ thống mà không mang lại lợi ích thực tế.

Luôn sử dụng công cụ như `EXPLAIN` để kiểm tra cách database thực thi query, từ đó xác định index có thực sự được sử dụng hay không.

---

## Tổng kết
Index = công cụ tối ưu query quan trọng nhất, nhưng phải dùng đúng cách theo pattern truy vấn.

# SQL là gì

## 1. Khái niệm

SQL (Structured Query Language) là ngôn ngữ dùng để **làm việc với cơ sở dữ liệu quan hệ (RDBMS)**.  
Nó cho phép truy vấn, thêm, sửa, xóa và quản lý dữ liệu.

---

## 2. Vai trò

- Giao tiếp giữa backend và database  
- Truy vấn và xử lý dữ liệu  
- Quản lý cấu trúc dữ liệu (table, index, constraint)

---

## 3. Các nhóm lệnh chính

### DML (Data Manipulation Language)
- `SELECT`: lấy dữ liệu  
- `INSERT`: thêm dữ liệu  
- `UPDATE`: cập nhật  
- `DELETE`: xóa  

---

### DDL (Data Definition Language)
- `CREATE`, `ALTER`, `DROP`

---

### TCL (Transaction Control Language)
- `BEGIN`, `COMMIT`, `ROLLBACK`

---

## 4. Transaction trong SQL

Transaction là cơ chế cho phép nhóm nhiều câu lệnh SQL thành **một đơn vị thực thi duy nhất**.

- Thành công → `COMMIT` (lưu toàn bộ)
- Thất bại → `ROLLBACK` (hủy toàn bộ)

### Ví dụ
```sql
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT; 
```

Mục tiêu: đảm bảo tính nhất quán của dữ liệu, tránh trường hợp một phần transaction thành công và phần còn lại thất bại.

# Caching

## 1. Tại sao cần cache

Cache được sử dụng để **tăng tốc độ truy xuất dữ liệu** và giảm tải cho database.

- Giảm số lần query database
- Giảm latency (trả kết quả nhanh hơn)
- Tăng khả năng chịu tải của hệ thống

---

## 2. Cache layer

Cache thường nằm giữa backend và database.

- Phổ biến: Redis
- Lưu dữ liệu dạng key-value
- Truy cập nhanh (in-memory)

Luồng:
```text
Client → Backend → Cache → Database
```
## 3. Cache invalidation

Cache không tự cập nhật → cần xóa hoặc cập nhật khi data thay đổi

Các cách:

- TTL (time-to-live)
- Xóa cache khi update data
- Versioning key

# NoSQL & Use Cases

## 1. Khái niệm

NoSQL là nhóm các database **không quan hệ**, không yêu cầu schema cố định và được thiết kế để scale tốt.

Phù hợp với:
- Dữ liệu lớn (big data)
- Dữ liệu linh hoạt, thay đổi thường xuyên
- Hệ thống cần scale cao

---

## 2. Các loại NoSQL phổ biến

### Key-value (Redis)

- Dữ liệu dạng: key → value
- Truy cập cực nhanh (in-memory)

**Use case:**
- Cache
- Session
- Rate limiting

---

### Document (MongoDB)

- Lưu dữ liệu dạng JSON (document)
- Schema linh hoạt

**Use case:**
- Dữ liệu không cố định
- CMS, log, user profile

---

### Column-family (Cassandra)

- Lưu theo cột (column-based)
- Scale ngang rất tốt

**Use case:**
- Big data
- Analytics
- Hệ thống phân tán lớn

---

## 3. Khi nào dùng NoSQL vs SQL

### Dùng SQL khi:

- Dữ liệu có cấu trúc rõ ràng
- Có quan hệ phức tạp (JOIN)
- Cần transaction (ACID)
- Ví dụ: user, order, payment

---

### Dùng NoSQL khi:

- Dữ liệu linh hoạt, thay đổi schema
- Scale lớn (horizontal scaling)
- Không cần join phức tạp
- Ví dụ: log, cache, analytics, realtime data

---

## Tổng kết

- SQL: strong consistency, phù hợp nghiệp vụ chính  
- NoSQL: flexible, scale tốt, phù hợp dữ liệu lớn  

→ Thực tế thường dùng kết hợp cả hai

# Scaling Database

## Vertical scaling
- Tăng CPU, RAM

## Horizontal scaling
- Sharding
- Replication:
  - Master - Slave
  - Read replica

---

# Database Security

## 1. Authentication DB

Xác thực truy cập database:

- User / password
- Role-based account (app user, admin…)
- Không dùng tài khoản root cho ứng dụng

→ Mục tiêu: chỉ cho phép các service hợp lệ truy cập DB

---

## 2. Encryption

Mã hóa dữ liệu để bảo vệ thông tin nhạy cảm:

- **In-transit**: SSL/TLS (HTTPS, DB connection)
- **At-rest**: mã hóa dữ liệu lưu trong DB

Ngoài ra:
- Hash password (bcrypt, argon2)
- Không lưu plain text

---

## 3. Access Control

Kiểm soát quyền truy cập dữ liệu:

- Phân quyền theo role:
  - Read
  - Write
  - Admin
- Giới hạn quyền theo table / schema

---

## Công nghệ liên quan
PostgreSQL, MySQL, MongoDB, Redis (cache), pgAdmin, Robo 3T, mongosh

## Tổng kết

Một backend engineer cần:
- Nắm chắc SQL + data modeling
- Hiểu transaction, index, optimization
- Biết cách scale và cache
- Chọn đúng loại database theo bài toán
