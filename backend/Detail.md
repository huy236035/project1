# Cấu trúc và Chức năng Backend

Tài liệu này liệt kê chi tiết các file mã nguồn trong thư mục `backend`, giải thích chức năng và vai trò của chúng trong hệ thống.

## 1. Core (Gốc Project)

### `app.py`
- **Vai trò**: Điểm khởi chạy chính (Entry Point) của ứng dụng Flask.
- **Chức năng**:
  - Khởi tạo Flask App.
  - Cấu hình CORS (cho phép Frontend gọi API).
  - Đăng ký các Blueprints (Routes).
  - Chạy server (mặc định port 5000).

### `config.py`
- **Vai trò**: Quản lý cấu hình toàn bộ hệ thống.
- **Chức năng**:
  - Đọc biến môi trường (Environment Variables).
  - Lưu các tham số thuật toán (GA_POPULATION_SIZE, GA_GENERATIONS).
  - Lưu cấu hình OSRM (URL, timeout).

---

## 2. API Layer (`api/`)

### `api/routes.py`
- **Vai trò**: Quản lý đăng ký Routing.
- **Chức năng**: Tập hợp các Blueprint và đăng ký vào Flask App. Giúp code gọn gàng, dễ mở rộng.

### `api/route_api.py`
- **Vai trò**: Xử lý logic nghiệp vụ cho API `/multi-route`.
- **Chức năng**:
  - Nhận request từ Frontend (JSON list các điểm).
  - Gọi `validate_coordinates` để kiểm tra dữ liệu.
  - Khởi tạo `RouteSolver` để tìm lời giải.
  - Trả về kết quả JSON chuẩn hóa (Success/Error).

---

## 3. Thuật toán & Logic (`thuat_toan/`)

### `thuat_toan/solver.py`
- **Vai trò**: Bộ não trung tâm điều phối thuật toán (Controller).
- **Chức năng**:
  1.  Gọi `OSRMService` để lấy Ma trận khoảng cách giữa tất cả các điểm.
  2.  Quyết định thuật toán sử dụng dựa trên kích thước bài toán (N):
      - **N ≤ 12**: Gọi `held_karp` (Chính xác).
      - **N > 12**: Gọi `genetic_algorithm` (Gần đúng).
  3.  Đo đạc thời gian thực thi (Profiling) cho việc gọi OSRM và chạy thuật toán.

### `thuat_toan/algorithms/genetic_algorithm.py`
- **Vai trò**: Giải quyết bài toán TSP lớn (N > 12).
- **Chức năng**:
  - Cài đặt thuật toán Di truyền (Genetic Algorithm): Khởi tạo quần thể, Lai ghép, Đột biến, Chọn lọc.
  - Tích hợp **2-Opt Local Search** để tinh chỉnh kết quả cuối cùng.
  - **Tối ưu hóa**: Truy cập trực tiếp ma trận khoảng cách (`matrix[i][j]`) thay vì tạo object trung gian, giúp tốc độ cực nhanh.

### `thuat_toan/algorithms/held_karp.py`
- **Vai trò**: Giải quyết bài toán TSP nhỏ (N ≤ 12).
- **Chức năng**:
  - Cài đặt thuật toán Held-Karp (Dynamic Programming).
  - Đảm bảo tìm ra lộ trình ngắn nhất tuyệt đối (Global Optimum).
  - Độ phức tạp $O(n^2 2^n)$, nên giới hạn N nhỏ.

---

## 4. Dịch vụ & Thông tin (`thong_tin/`)

### `thong_tin/osrm_service.py`
- **Vai trò**: Cổng giao tiếp với OSRM Server.
- **Chức năng**:
  - Gửi request đến endpoint `/table/v1/driving`.
  - Chuyển đổi response JSON từ OSRM thành ma trận khoảng cách $N \times N$ để thuật toán Python sử dụng.
  - Xử lý lỗi kết nối/timeout.

### `thong_tin/data_validator.py`
- **Vai trò**: Kiểm tra tính hợp lệ dữ liệu đầu vào.
- **Chức năng**: Đảm bảo các điểm gửi lên có đủ `lat`, `lng` và nằm trong phạm vi hợp lệ.

---

## 5. Tiện ích (`utils/`)

### `utils/logger.py`
- **Vai trò**: Hệ thống ghi log tập trung.
- **Chức năng**: Cung cấp logger chuẩn để ghi lại quá trình chạy, lỗi, và thông tin debug ra Console/File.
