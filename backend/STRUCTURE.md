# Cấu trúc Backend - Tổng quan

## Mô tả các folder chính

### 📁 `api/` - API Routes
Chứa tất cả các API endpoints:
- `route_api.py`: API tìm đường đi (GET /api/route, POST /api/multi-route)
- `routes.py`: Đăng ký tất cả routes vào Flask app

### 📁 `thong_bao_trang_thai/` - Thông báo & Trạng thái
Xử lý thông báo và quản lý trạng thái request:
- `notification_service.py`: Gửi thông báo cho người dùng (email, push, SMS)
- `status_service.py`: Quản lý trạng thái request (pending, processing, completed, failed)
- `message_handler.py`: Xử lý và format các loại message khác nhau

### 📁 `thong_tin/` - Thông tin & Dữ liệu điểm
Xử lý dữ liệu địa chỉ và vị trí người dùng chọn:
- `address_handler.py`: Xử lý địa chỉ các điểm người dùng chọn
- `location_service.py`: Service quản lý vị trí, chuyển đổi địa chỉ sang nodes
- `data_validator.py`: Validate dữ liệu đầu vào (tọa độ, địa chỉ)
- `models/`: Các model dữ liệu (Location, Address)

### 📁 `map/` - Bản đồ Hà Nội
Xử lý dữ liệu bản đồ và thông tin giao thông:
- `map_loader.py`: Load dữ liệu bản đồ từ OSM hoặc file
- `traffic_handler.py`: Xử lý thông tin tắc đường (real-time hoặc static)
- `road_network.py`: Quản lý mạng lưới đường
- `map_data_service.py`: Service cung cấp dữ liệu bản đồ cho Solver
- `data/`: Dữ liệu bản đồ Hà Nội (nodes, traffic)

### 📁 `thuat_toan/` - Thuật toán
Chứa các thuật toán tìm đường đi:
- `solver.py`: **File Solver chính** - Kết hợp A* và GA để tìm đường đi ngắn nhất
- `algorithms/`: Các thuật toán riêng lẻ
  - `astar.py`: Thuật toán A* tìm đường đi ngắn nhất giữa 2 điểm
  - `genetic_algorithm.py`: Thuật toán GA tối ưu thứ tự các điểm
  - `dijkstra.py`: Thuật toán Dijkstra (backup)
- `utils/`: Utilities cho thuật toán
  - `graph.py`: Class Graph quản lý đồ thị
  - `path_converter.py`: Chuyển đổi path sang coordinates
  - `distance_calculator.py`: Tính toán khoảng cách (Haversine)

### 📁 `ket_qua/` - Kết quả & Response
Format và xây dựng response:
- `result_formatter.py`: Format kết quả trả về
- `response_builder.py`: Xây dựng response JSON chuẩn

### 📁 `tests/` - Test files
Tất cả file test tập trung ở đây:
- `test_astar.py`: Test thuật toán A*
- `test_genetic_algorithm.py`: Test thuật toán GA
- `test_multi_point.py`: Test multi-point routing
- `test_solver.py`: Test Solver chính

### 📁 `utils/` - Utilities chung
Các utility functions dùng chung:
- `exceptions.py`: Custom exceptions
- `logger.py`: Logging utility
- `helpers.py`: Helper functions

## Luồng xử lý chính

1. **API Request** → `api/route_api.py`
2. **Validate dữ liệu** → `thong_tin/data_validator.py`
3. **Chuyển đổi địa chỉ** → `thong_tin/location_service.py`
4. **Lấy dữ liệu bản đồ** → `map/map_data_service.py`
5. **Tính toán route** → `thuat_toan/solver.py`
   - Sử dụng A* để tính ma trận khoảng cách
   - Sử dụng GA để tối ưu thứ tự các điểm
6. **Format kết quả** → `ket_qua/result_formatter.py`
7. **Trả về response** → `ket_qua/response_builder.py`

## Cách sử dụng Solver

```python
from thuat_toan.solver import RouteSolver
from thong_tin.models.location import Location

# Tạo solver
solver = RouteSolver(consider_traffic=True)

# Tạo danh sách địa điểm
locations = [
    Location(lat=21.0285, lng=105.8542, name="Hồ Gươm"),
    Location(lat=21.0300, lng=105.8560, name="Điểm B"),
    Location(lat=21.0320, lng=105.8520, name="Điểm C"),
]

# Giải
result = solver.solve(locations, ga_population_size=100, ga_generations=500)

# Kết quả
print(f"Route: {result['route']}")
print(f"Distance: {result['distance']} km")
print(f"Path coordinates: {result['path_coordinates']}")
```

## Lợi ích của cấu trúc mới

✅ **Tách biệt rõ ràng**: Mỗi folder có trách nhiệm riêng  
✅ **Dễ bảo trì**: Dễ tìm và sửa code  
✅ **Dễ mở rộng**: Thêm tính năng mới không ảnh hưởng code cũ  
✅ **Dễ test**: Test từng module độc lập  
✅ **Dễ làm việc nhóm**: Mỗi người có thể làm việc trên folder riêng  
✅ **Code rõ ràng**: Tên folder và file dễ hiểu, dễ theo dõi

