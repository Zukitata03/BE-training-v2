# Module 3 — Xác thực & Ủy quyền (Authentication & Authorization)

## Authentication vs Authorization & Common Flows

---

## 1. Authentication vs Authorization

### Authentication (AuthN) – Xác minh danh tính  
Là quá trình xác định danh tính của một thực thể (user, service).  
Trả lời câu hỏi: **“Bạn là ai?”**

**Đặc điểm:**
- Dựa trên thông tin định danh: username/password, OTP, token, certificate  
- Kết quả là một identity (ví dụ: user_id, subject)  
- Thường sinh ra credential (session hoặc token)  

---

### Authorization (AuthZ) – Phân quyền truy cập  
Là quá trình xác định quyền của thực thể sau khi đã được xác thực.  
Trả lời câu hỏi: **“Bạn được phép làm gì?”**

**Đặc điểm:**
- Dựa trên role, permission hoặc policy  
- Áp dụng tại từng resource hoặc action cụ thể  
- Luôn xảy ra sau authentication  

---

### Mối quan hệ
- Authentication → xác định danh tính  
- Authorization → kiểm tra quyền truy cập  
- Authorization luôn phụ thuộc vào Authentication  

---

## 2. Các Flow phổ biến

---

## 2.1 Session-based Authentication

### Khái niệm  
Cơ chế xác thực dựa trên session lưu ở phía server. Client giữ session_id để tham chiếu.

### Flow
1. User gửi thông tin đăng nhập  
2. Server xác thực → tạo session  
3. Session lưu trong DB hoặc Redis  
4. Server trả về session_id qua cookie  
5. Các request tiếp theo:
   - Client gửi cookie  
   - Server lookup session → xác thực  

### Đặc điểm
- Stateful (có lưu trạng thái)  
- Server kiểm soát hoàn toàn session  

---

### Ưu điểm
- Dễ revoke (chỉ cần xóa session ở server)  
- Bảo mật tốt khi dùng httpOnly cookie  
- Không expose dữ liệu user ra client  
- Dễ implement cho hệ thống monolith  

---

### Nhược điểm
- Stateful → cần lưu session (DB/Redis)  
- Khó scale (cần shared session store)  
- Tăng latency do phải lookup session mỗi request  
- Phụ thuộc vào hạ tầng (Redis, replication, HA)  

---

## 2.2 Token-based Authentication (JWT)

### Khái niệm  
Cơ chế xác thực sử dụng token (thường là JWT), không cần lưu trạng thái phía server.

### Flow
1. User đăng nhập  
2. Server tạo JWT chứa thông tin user  
3. Client lưu token  
4. Mỗi request:
   - Gửi Authorization: Bearer token  
5. Server verify chữ ký và thời hạn token  

### Đặc điểm
- Stateless (không cần lưu session)  
- Token chứa thông tin (self-contained)  

---

### Ưu điểm
- Stateless → không cần lưu session  
- Scale tốt cho microservices  
- Không cần DB lookup mỗi request  
- Dễ chia sẻ giữa nhiều service (SSO, distributed system)  

---

### Nhược điểm
- Khó revoke (token vẫn hợp lệ đến khi hết hạn)  
- Nếu bị lộ → attacker dùng được ngay  
- Payload không mã hóa (chỉ encode)  
- Token lớn → tăng overhead network  
- Phức tạp hơn khi cần refresh, rotate, blacklist  

---

## 2.3 OAuth2

### Khái niệm  
Chuẩn dùng để **ủy quyền (authorization)** giữa các hệ thống hoặc bên thứ ba.

### Thành phần
- Resource Owner (User)  
- Client (ứng dụng)  
- Authorization Server  
- Resource Server  

---

### Authorization Code Flow
1. Client redirect user đến Authorization Server  
2. User đăng nhập và đồng ý cấp quyền  
3. Server trả về authorization_code  
4. Client dùng code để lấy access_token  

---

### Client Credentials Flow
1. Service gửi client_id và client_secret  
2. Nhận access_token  
3. Dùng token để gọi API  

---

## 2.4 OpenID Connect (OIDC)

### Khái niệm  
Là lớp mở rộng trên OAuth2 để hỗ trợ **authentication**.

### Đặc điểm
- Cung cấp ID Token (JWT)  
- Chuẩn hóa thông tin user (email, name, subject)  

---

### Flow
- Tương tự OAuth2  
- Ngoài access_token còn có thêm ID Token  

---

## 3. So sánh tổng quan

| Cơ chế | Stateful | Mục đích chính | Use case |
|--------|--------|---------------|----------|
| Session | Có | Authentication | Web truyền thống |
| JWT | Không | Authentication | API, microservices |
| OAuth2 | Không | Authorization | Third-party access |
| OIDC | Không | Authentication | SSO, social login |

---

## 4. Tổng kết

- Authentication xác định danh tính của user hoặc service  
- Authorization xác định quyền truy cập tài nguyên  
- Session-based phù hợp hệ thống đơn giản, dễ quản lý  
- JWT phù hợp hệ thống phân tán, cần scale  
- OAuth2 dùng cho ủy quyền giữa các hệ thống  
- OIDC bổ sung khả năng xác thực chuẩn hóa trên OAuth2

## Công nghệ liên quan
bcrypt, argon2, PyJWT, OAuth2 libraries (Authlib), Keycloak, IdentityServer, OpenID Connect
