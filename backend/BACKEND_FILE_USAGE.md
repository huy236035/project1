## Tổng quan sử dụng file trong Backend

Tài liệu này liệt kê **các file đang được sử dụng trong luồng chạy chính** của Backend, các file **hỗ trợ / test / tài liệu**, và các file **hiện tại không còn được dùng trong luồng API chính** (có thể coi là legacy).

---

## 1. Nhóm file đang dùng trong luồng API chính

### 1.1. Entry point & cấu hình
- `app.py`  
  - Entry point Flask (`py -3 app.py`).
  - Tạo `Flask` app, cấu hình CORS, đăng ký routes, tạo endpoint `/health`.

- `config.py`  
  - Chứa `Config` (PORT, HOST, DEBUG, CORS_ORIGINS, ...).  
  - Được dùng bởi `app.py` và có thể bởi các module khác.

- `utils/logger.py`  
  - Cấu hình logger dùng chung.
  - Được import và dùng trong nhiều nơi: `app.py`, `route_api.py`, `solver.py`, `map_data_service.py`, `osm_service.py`, v.v.

### 1.2. API layer
- `api/routes.py`  
  - Hàm `register_routes(app)` đăng ký blueprint `route_bp` với prefix `/api`.

- `api/route_api.py`  
  - Định nghĩa các endpoint chính:
    - `GET /api/route`: tìm đường giữa 2 node ID (dùng `RouteSolver` + A* + `MapDataService`).
    - `POST /api/multi-route`: nhận danh sách tọa độ GPS, gọi `RouteSolver.solve_from_coordinates()` để tìm **thứ tự tối ưu**.
  - Sử dụng:
    - `RouteSolver` từ `thuat_toan/solver.py`.
    - `DataValidator` từ `thong_tin/data_validator.py`.
    - `ResponseBuilder` từ `ket_qua/response_builder.py`.
    - `logger` và các custom exceptions từ `utils/`.

### 1.3. Tầng xử lý thông tin & validate
- `thong_tin/data_validator.py`  
  - Validate dữ liệu đầu vào cho API (tọa độ, mảng `points`, v.v.).  
  - Được dùng trực tiếp trong `api/route_api.py`.

- `thong_tin/models/location.py`  
  - Định nghĩa model `Location` (lat, lng, name, node_id, ...).  
  - Được dùng trong:
    - `thuat_toan/solver.py` (phiên bản `solve(locations)` dùng `Location`).
    - Các ví dụ trong tài liệu (`CONNECTION_FLOW.md`, `STRUCTURE.md`, tests).

- `thong_tin/location_service.py`  
  - Service chuyển tọa độ người dùng → node ID trong graph.  
  - Sử dụng `map_service` để tìm node gần nhất.  
  - Được dùng trong `RouteSolver.solve()` với dữ liệu kiểu `Location`.
  - Lưu ý: luồng `/api/multi-route` hiện tại đi qua `solve_from_coordinates()` (không dùng `LocationService`), nhưng `solve()` vẫn có thể dùng cho các use-case khác / tests.

### 1.4. Tầng bản đồ & OSM
- `map/map_data_service.py`  
  - Service trung tâm để load graph OSM, traffic, node coordinates.
  - Dùng:
    - `map_loader.py` / `osm_loader.py` / `osm_service.py` để load từ OSM.
    - `TrafficHandler` để áp dụng hệ số tắc đường.
    - `RoadNetwork` để wrap graph.
  - Được dùng trong `RouteSolver` (cho `solve()` và `GET /api/route`).

- `map/map_loader.py`  
  - Hàm `load_map_from_osm`, `load_hanoi_map` sử dụng `OSMLoader` để load graph từ OSM.  
  - Được dùng trong `map_data_service.py` và trong tests (`tests/test_osm_loader.py`).

- `map/osm_loader.py`  
  - Class `OSMLoader` dùng `osmnx` để tải network từ OSM dưới nhiều dạng (place, bbox, point).  
  - Có hàm convert sang `Graph` custom.  
  - Được dùng trong: `map_loader.py`, `map_data_service.py`, `map/data/hanoi_nodes.py`, tests.

- `map/osm_service.py`  
  - Wrapper tối ưu hơn để load dữ liệu OSM, cache, convert sang `Graph` + node coordinates đồng bộ.  
  - Được dùng trong `map_data_service.py` (`_load_graph_and_coordinates_from_osm()`).

- `map/traffic_handler.py` + `map/data/traffic_data.py`  
  - Cung cấp hệ số tắc đường cho từng node.  
  - `TrafficHandler` được dùng trong `map_data_service.py` để nhân hệ số vào trọng số cạnh khi consider_traffic = True.

- `map/road_network.py`  
  - Wrap `Graph` để biểu diễn mạng lưới đường.  
  - Dùng trong `map_data_service.py`.

> Nhận xét: Toàn bộ `map/*` tạo thành subsystem OSM/graph. Đối với luồng `/api/multi-route` hiện tại chỉ cần GA + haversine, nhưng `map_data_service` vẫn được sử dụng cho `solve()` và `/api/route`.

### 1.5. Tầng thuật toán (A*, GA, Graph)
- `thuat_toan/solver.py`  
  - **Trái tim của backend**.
  - Hai đường vào chính:
    - `solve(locations: List[Location])`: sử dụng `MapDataService` + `LocationService` + A* + GA, trả về cả route và `path_coordinates` + `detailed_paths`. Dùng cho luồng cũ/đầy đủ.
    - `solve_from_coordinates(coordinates: List[Dict])`: sử dụng `Graph` + `haversine_distance` + GA, **không cần OSM**, trả về **route indices** cho frontend gọi OSM Routing API.
  - Dùng các module:
    - `thuat_toan/algorithms/astar.py`
    - `thuat_toan/algorithms/genetic_algorithm.py`
    - `thuat_toan/utils/graph.py`
    - `thuat_toan/utils/distance_calculator.py`

- `thuat_toan/algorithms/astar.py`  
  - Thuật toán A* dùng để:
    - Tính đường đi giữa 2 node (cho `/api/route`).
    - Tính ma trận khoảng cách giữa các node trong `solve()`.
  - Hỗ trợ `node_coordinates` để tính heuristic theo haversine.

- `thuat_toan/algorithms/genetic_algorithm.py`  
  - GA tối ưu thứ tự các điểm (TSP-like).  
  - Được gọi trong cả `solve()` và `solve_from_coordinates()`.

- `thuat_toan/utils/graph.py`  
  - Class `Graph` cơ bản (nodes, edges, weights).  
  - Được dùng rất nhiều: trong solver, A*, GA, map loader, OSM loader.

- `thuat_toan/utils/distance_calculator.py`  
  - Hàm `haversine_distance(...)` dùng cho:
    - Heuristic trong A* (khi có node_coordinates).
    - Tính khoảng cách trực tiếp trong `solve_from_coordinates()`.

- `thuat_toan/utils/path_converter.py`  
  - Chuyển path node IDs → list tọa độ, dùng trong `/api/route` (2 điểm) để trả `path` cho frontend.

### 1.6. Tầng format kết quả
- `ket_qua/result_formatter.py`  
  - Format dữ liệu thô từ solver thành cấu trúc dễ đọc hơn (khoảng cách, route, v.v.).  

- `ket_qua/response_builder.py`  
  - Tạo JSON response chuẩn cho API (success, error, HTTP code).  
  - Được dùng trong `api/route_api.py`.

### 1.7. Utils chung
- `utils/exceptions.py`  
  - Định nghĩa `InvalidCoordinatesException`, `NoPathFoundException`, ...  
  - Được dùng trong `route_api.py` và các chỗ khác để throw lỗi cụ thể.

- `utils/helpers.py`  
  - Helper functions dùng chung (nếu còn được reference trong code).  

---

## 2. Nhóm file hỗ trợ: tests, scripts, docs

### 2.1. Tests
- `tests/test_astar.py`  
  - Test thuật toán A* với `Graph` và `nodes_to_coordinates`.

- `tests/test_genetic_algorithm.py`  
  - Test GA hoạt động đúng với `Graph` giả lập.

- `tests/test_multi_point.py`  
  - Test luồng solver với nhiều điểm (multi-route).

- `tests/test_solver.py`  
  - Test trực tiếp `RouteSolver` với dữ liệu mẫu.

- `tests/test_osm_loader.py`  
  - Test `OSMLoader` + `map_loader` + `map_data_service` khi có OSM.

> Các file này **không chạy trong production**, nhưng **nên giữ** để test & debug.

### 2.2. Scripts & Run files
- `run.bat`, `run.ps1`, `RUN.md`  
  - Script / tài liệu để chạy backend nhanh trên Windows.

### 2.3. Docs nội bộ
- `README.md` (backend)  
  - Mô tả tổng quan backend, cấu trúc, cách chạy.

- `STRUCTURE.md`  
  - Mô tả chi tiết cấu trúc thư mục backend và luồng xử lý.

- `CONNECTION_FLOW.md`  
  - Diễn giải luồng kết nối Map ↔ Người dùng ↔ Thuật toán theo phiên bản kiến trúc cũ (dùng OSM ở backend).
  - Một số phần trong file này hiện **không còn đúng hoàn toàn** với kiến trúc mới (frontend gọi OSM Routing API), nhưng vẫn hữu ích để hiểu lịch sử phát triển.

- `OSM_SETUP.md`  
  - Hướng dẫn cài đặt `osmnx`, `geopandas`, ... nếu muốn backend trực tiếp load OSM.

---

## 3. Nhóm file hiện **không còn dùng trong luồng API chính**

Những file này **không được import hoặc sử dụng trực tiếp** trong `app.py` → `api/route_api.py` → `RouteSolver.solve_from_coordinates()` (luồng đang chạy thực tế cho FE).

Chúng có thể:
- Chỉ được nhắc tới trong docs/tests.
- Là phần kiến trúc cũ (vd: sample data, hệ thống thông báo).

### 3.1. Module thông báo trạng thái (chưa được dùng)
- `thong_bao_trang_thai/message_handler.py`
- `thong_bao_trang_thai/notification_service.py`
- `thong_bao_trang_thai/status_service.py`

Hiện tại:
- Không có file nào trong `api/`, `app.py`, `solver.py` import `thong_bao_trang_thai.*`.
- Chỉ xuất hiện trong tài liệu (`README.md`, `STRUCTURE.md`).  
👉 Có thể coi là **module chuẩn bị cho future feature**, chưa được tích hợp vào luồng chạy hiện tại.

### 3.2. Dữ liệu sample Hà Nội cũ
- `map/data/hanoi_nodes.py`

Trước đây:
- Dùng làm sample data khi chưa có OSM hoặc để test nhanh.

Hiện tại:
- Không có file code nào import trực tiếp `map.data.hanoi_nodes` (chỉ còn trong `README.md`, `CONNECTION_FLOW.md`).  
👉 Có thể coi là **legacy sample**, không còn được dùng trong luồng chạy chính.

### 3.3. Utility không được tham chiếu
- `utils/coordinate_multi_route.py`

Hiện tại:
- Không tìm thấy nơi nào trong backend import file này.
- Có vẻ là utility thử nghiệm/nháp cho multi-route trước đây.  
👉 Có thể xoá hoặc chuyển sang thư mục `sandbox/` / `legacy/` nếu muốn dọn code.

---

## 4. Gợi ý dọn dẹp / refactor

Nếu mục tiêu là **backend nhẹ nhất, chỉ làm TSP và để FE gọi OSM Routing API**, có thể cân nhắc:

1. **Giữ bắt buộc** (core luồng multi-route hiện tại):
   - `app.py`, `config.py`
   - `api/route_api.py`, `api/routes.py`
   - `thuat_toan/solver.py` (đặc biệt `solve_from_coordinates`)
   - `thuat_toan/algorithms/genetic_algorithm.py`
   - `thuat_toan/utils/graph.py`, `thuat_toan/utils/distance_calculator.py`
   - `thong_tin/data_validator.py`
   - `ket_qua/response_builder.py`
   - `utils/logger.py`, `utils/exceptions.py`

2. **Giữ nếu còn dùng `/api/route` (2 điểm, đường chi tiết từ backend)**:
   - `map/*` (map_data_service, osm_loader, osm_service, road_network, traffic_handler, traffic_data)
   - `thuat_toan/algorithms/astar.py`
   - `thuat_toan/utils/path_converter.py`
   - `thong_tin/location_service.py`, `thong_tin/models/location.py`

3. **Có thể tách/đánh dấu là legacy / optional**:
   - `thong_bao_trang_thai/*`
   - `map/data/hanoi_nodes.py`
   - `utils/coordinate_multi_route.py`
   - Các đoạn docs trong `CONNECTION_FLOW.md` mô tả kiến trúc cũ (backend tự load OSM và trả path_coordinates).

---

## 5. Kết luận

- Luồng hiện tại FE → BE cho multi-route chủ yếu dùng **GA + haversine** trong `solve_from_coordinates` và **không bắt buộc backend phải load OSM**.
- Subsystem `map/*` và A* vẫn tồn tại để:
  - Hỗ trợ endpoint `/api/route` theo kiểu truyền thống.
  - Giữ khả năng mở rộng nếu sau này muốn chuyển logic OSM về backend.
- Một số module (`thong_bao_trang_thai`, `hanoi_nodes`, `coordinate_multi_route`) hiện không chạy trong flow chính, có thể coi là **legacy/feature dự phòng** và dọn dẹp sau nếu muốn codebase gọn hơn.


