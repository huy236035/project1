# Hệ thống Tối ưu Lộ trình (TSP Solver for Vietnam)

Dự án Web App giúp tìm lộ trình đi qua nhiều điểm ngắn nhất (Traveling Salesman Problem - TSP) sử dụng kết hợp thuật toán **Genetic Algorithm (Di truyền)** và **Held-Karp** (Quy hoạch động) trên nền tảng bản đồ **OpenStreetMap (OSRM)**.

## 🚀 Tính năng chính
- Tìm đường đi ngắn nhất qua nhiều điểm (lên tới 50+ điểm).
- Tự động chọn thuật toán tối ưu dựa trên số lượng điểm:
  - **N ≤ 12**: Held-Karp
  - **N > 12**: Genetic Algorithm + 2-Opt
- Hiển thị bản đồ trực quan với Leaflet và OpenStreetMap.
- Hỗ trợ xem chi tiết từng chặng đường (khoảng cách, đường đi).
- **Tối ưu hiệu năng**: Sử dụng OSRM Table API và xử lý ma trận trực tiếp giúp thời gian tính toán < 1s.

## 🛠️ Cài đặt & Chạy thử

### Yêu cầu
- **Python 3.8+**
- **Node.js 14+**
- **Docker Desktop** (Tùy chọn - nếu muốn chạy OSRM Local để đạt tốc độ tối đa).

### 1. Khởi chạy Backend (Python/Flask)
```bash
# Di chuyển vào thư mục backend
cd backend

# Cài đặt thư viện (nên dùng virtualenv)
pip install -r ../requirements.txt

# Chạy server
py app.py
# Server sẽ chạy tại: http://localhost:5000
```

### 2. Khởi chạy Frontend (ReactJS)
```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install

# Chạy ứng dụng
npm start
# App sẽ chạy tại: http://localhost:3000
```

## ⚙️ Cấu hình (Optional)
File cấu hình Backend nằm tại `backend/config.py`. Bạn có thể thay đổi các tham số thuật toán di truyền như `GA_POPULATION_SIZE`, `GA_GENERATIONS` tại đây.

## 🐳 Chạy OSRM Local (Khuyên dùng)
Để đạt tốc độ tính toán nhanh nhất (tránh network latency sang server quốc tế), bạn nên chạy OSRM Server tại máy cục bộ bằng Docker.

---
**Tác giả:** Dương Gia Huy - 20236035
**Dự án học phần:** Project 1
