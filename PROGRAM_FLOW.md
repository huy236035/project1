# Luồng Chương Trình và Dữ Liệu (Data Flow)

## Sơ đồ tóm tắt
```mermaid
graph TD
    User[Người dùng] -->|1. Chọn điểm| FE[Frontend (React)]
    FE -->|2. Gửi request (Points)| BE[Backend (Flask)]
    
    subgraph Backend Steps
        BE -->|3. Get Distance Matrix| OSRM_Table[OSRM Table API]
        OSRM_Table -->|Matrix| BE
        BE -->|4. Tính toán (Solver)| Algo{Chọn Thuật toán}
        Algo -->|N <= 12| HK[Held-Karp]
        Algo -->|N > 12| GA[Genetic Algorithm]
        HK --> Result
        GA --> Result
    end
    
    Result -->|5. Trả về Route (Indices)| FE
    FE -->|6. Get Geometry| OSRM_Route[OSRM Route API]
    OSRM_Route -->|Shape/Polyline| FE
    FE -->|7. Hiển thị| User
```

## Chi tiết từng bước

### 1. Thu thập dữ liệu (Frontend)
- **Hành động**: Người dùng click vào bản đồ để chọn các điểm cần đi qua.
- **Dữ liệu**: `Map.js` lưu danh sách các điểm `selectedPoints`:
  ```json
  [
    {"id": 1, "lat": 21.02, "lng": 105.85},
    {"id": 2, "lat": 21.03, "lng": 105.84}
  ]
  ```

### 2. Gửi yêu cầu tối ưu (Frontend -> Backend)
- **Hành động**: Người dùng bấm nút **"Tìm đường"**.
- **Request**: `api.js` gửi `POST` đến `http://localhost:5000/api/multi-route`.
- **Payload**:
  ```json
  {
    "points": [
      {"lat": 21.02, "lng": 105.85},
      {"lat": 21.03, "lng": 105.84},
      ...
    ],
    "consider_traffic": true,
    "ga_population_size": 100
  }
  ```

### 3. Xử lý Logic (Backend)
Backend nhận request và thực hiện chuỗi xử lý trong `solver.py`:
1.  **Lấy Ma trận khoảng cách**: Gọi **OSRM Table API** để lấy ma trận khoảng cách giữa tất cả các cặp điểm.
    -   *Input*: N điểm.
    -   *Output*: Ma trận $N \times N$ (đơn vị mét).
2.  **Chọn thuật toán**:
    -   Nếu $N \le 12$: Dùng **Held-Karp** (Quy hoạch động) để tìm nghiệm chính xác tuyệt đối.
    -   Nếu $N > 12$: Dùng **Genetic Algorithm (Di truyền)** kết hợp **2-Opt Local Search** để tìm nghiệm tối ưu gần đúng nhanh chóng.
3.  **Kết quả**: Thuật toán trả về thứ tự index tối ưu (ví dụ: `0 -> 2 -> 1 -> 0`).

### 4. Trả về kết quả (Backend -> Frontend)
- **Response**: Backend trả về JSON:
  ```json
  {
    "success": true,
    "route": [0, 2, 1, 0],  // Thứ tự index của các điểm trong mảng input
    "distance": 15.5,       // Tổng khoảng cách (km)
    "message": "Tối ưu thành công bằng..."
  }
  ```

### 5. Hiển thị đường đi (Frontend)
- **Xử lý**: 
    - Frontend nhận danh sách `route` (các chỉ số index).
    - Sắp xếp lại mảng `selectedPoints` theo thứ tự này.
- **Vẽ đường (Visualization)**:
    - Frontend gửi **1 Request duy nhất** chứa chuỗi tọa độ đã sắp xếp đến **OSRM Route API** (`/route/v1/driving/...`).
    - *Mục đích*: Lấy `geometry` (tọa độ chi tiết từng khúc cua) để vẽ đường xanh liền mạch lên bản đồ.
- **Kết quả**:
    - Bản đồ hiển thị đường nối qua tất cả các điểm.
    - Panel bên trái hiện chi tiết từng chặng và tổng quãng đường.
