# Luồng kết nối dữ liệu Map và Người dùng với Thuật toán

## Tổng quan

Tài liệu này mô tả cách dữ liệu từ **Map (OSM)** và **Người dùng** được kết nối với **Thuật toán** để tìm đường đi.

## Luồng xử lý

```
API Request (tọa độ người dùng)
    ↓
[thong_tin/data_validator.py] - Validate dữ liệu
    ↓
[thong_tin/models/location.py] - Tạo Location objects
    ↓
[thuat_toan/solver.py] - RouteSolver
    ├─→ [map/map_data_service.py] - Lấy graph từ OSM/sample
    │       ├─→ [map/osm_loader.py] - Load từ OSM
    │       └─→ [map/data/hanoi_nodes.py] - Fallback sample data
    │
    └─→ [thong_tin/location_service.py] - Chuyển đổi tọa độ → nodes
            └─→ Tìm node gần nhất từ map_service
    ↓
[thuat_toan/algorithms/astar.py] - Tính ma trận khoảng cách
    ↓
[thuat_toan/algorithms/genetic_algorithm.py] - Tối ưu thứ tự
    ↓
[thuat_toan/solver.py] - Xây dựng đường đi chi tiết
    ↓
[ket_qua/result_formatter.py] - Format kết quả
    ↓
API Response (route + coordinates)
```

## Chi tiết các bước

### 1. API nhận request từ người dùng

**File:** `api/route_api.py`

```python
# Người dùng gửi tọa độ
points = [
    {"lat": 21.0285, "lng": 105.8542},
    {"lat": 21.0300, "lng": 105.8560}
]

# Validate
DataValidator.validate_coordinates(points)

# Tạo solver
solver = RouteSolver(consider_traffic=True)
```

### 2. Solver khởi tạo MapDataService

**File:** `thuat_toan/solver.py`

```python
self.map_service = MapDataService()  # Load từ OSM hoặc sample
self.location_service = LocationService(map_service=self.map_service)
```

**MapDataService làm gì:**
- Load graph từ OSM (nếu `use_osm=True`)
- Hoặc load từ sample data (nếu `use_osm=False`)
- Lưu node coordinates vào `self.node_coordinates`
- Cung cấp graph cho thuật toán

### 3. LocationService chuyển đổi tọa độ → nodes

**File:** `thong_tin/location_service.py`

```python
# Tìm node gần nhất với mỗi tọa độ
node_id = self._find_nearest_node(lat, lng)

# Ưu tiên tìm từ map_service (OSM data)
if self.map_service:
    node_id = self.map_service.find_nearest_node(lat, lng)
```

**LocationService làm gì:**
- Nhận tọa độ từ người dùng
- Tìm node gần nhất trong graph (từ OSM hoặc sample)
- Trả về node_id để sử dụng trong thuật toán

### 4. Solver sử dụng graph và nodes

**File:** `thuat_toan/solver.py`

```python
# 1. Lấy graph từ map service
graph = self.map_service.get_graph(self.consider_traffic)

# 2. Chuyển đổi tọa độ → nodes
nodes = self.location_service.addresses_to_nodes(locations)

# 3. Tính ma trận khoảng cách bằng A*
distance_matrix = self._calculate_distance_matrix(graph, nodes)

# 4. Tối ưu thứ tự bằng GA
ga_result = genetic_algorithm(complete_graph, nodes, ...)

# 5. Xây dựng đường đi chi tiết
detailed_paths = self._build_detailed_path(graph, ga_result['route'])

# 6. Lấy tọa độ từ map_service
path_coordinates = self._build_path_coordinates(ga_result['route'])
```

### 5. Lấy tọa độ từ map_service

**File:** `thuat_toan/solver.py` - `_build_path_coordinates()`

```python
# Lấy từ map_service (có thể là OSM hoặc sample)
node_coords = self.map_service.get_all_node_coordinates()

for node_id in route:
    if node_id in node_coords:
        path_coordinates.append(node_coords[node_id])
```

## Kết nối giữa các module

### MapDataService ↔ LocationService

```python
# LocationService nhận map_service
location_service = LocationService(map_service=map_service)

# LocationService sử dụng map_service để:
# 1. Tìm node gần nhất
node_id = map_service.find_nearest_node(lat, lng)

# 2. Lấy tọa độ node
coords = map_service.get_node_coordinates(node_id)
```

### MapDataService ↔ Solver

```python
# Solver nhận graph từ map_service
graph = map_service.get_graph(consider_traffic=True)

# Solver lấy node coordinates
node_coords = map_service.get_all_node_coordinates()
```

### LocationService ↔ Solver

```python
# Solver sử dụng location_service để chuyển đổi tọa độ
nodes = location_service.addresses_to_nodes(locations)

# LocationService được khởi tạo với map_service
location_service = LocationService(map_service=map_service)
```

## Xử lý OSM vs Sample Data

### Khi load từ OSM:

1. **MapDataService** load graph từ OSM
2. Lưu node coordinates từ OSM (node_id là OSM IDs - số)
3. **LocationService** tìm node gần nhất từ OSM graph
4. **Solver** sử dụng OSM graph và OSM node IDs

### Khi load từ Sample:

1. **MapDataService** load graph từ sample data
2. Lưu node coordinates từ `hanoi_nodes.py` (node_id là "A", "B", "C", "D")
3. **LocationService** tìm node gần nhất từ sample nodes
4. **Solver** sử dụng sample graph và sample node IDs

## Ví dụ luồng hoàn chỉnh

```python
# 1. Người dùng gửi request
POST /api/multi-route
{
    "points": [
        {"lat": 21.0285, "lng": 105.8542},  # Hồ Gươm
        {"lat": 21.0300, "lng": 105.8560}   # Điểm khác
    ]
}

# 2. API validate và tạo solver
solver = RouteSolver()

# 3. Solver khởi tạo
map_service = MapDataService(use_osm=True)  # Load từ OSM
location_service = LocationService(map_service=map_service)

# 4. Chuyển đổi tọa độ → nodes
locations = [Location(lat=21.0285, lng=105.8542), ...]
nodes = location_service.addresses_to_nodes(locations)
# nodes = ["123456", "789012"]  # OSM node IDs

# 5. Lấy graph
graph = map_service.get_graph(consider_traffic=True)

# 6. Tính toán route
result = solver.solve(locations)

# 7. Lấy tọa độ từ map_service
path_coordinates = map_service.get_all_node_coordinates()
# path_coordinates = {"123456": {"lat": 21.0285, "lng": 105.8542}, ...}

# 8. Trả về kết quả
{
    "route": ["123456", "789012"],
    "distance": 2.5,
    "path_coordinates": [
        {"lat": 21.0285, "lng": 105.8542},
        {"lat": 21.0300, "lng": 105.8560}
    ]
}
```

## Kiểm tra kết nối

Để kiểm tra xem kết nối đã hoạt động chưa:

1. **Test MapDataService:**
```python
from map.map_data_service import MapDataService
service = MapDataService(use_osm=True)
graph = service.get_graph()
print(f"Graph có {len(list(graph.get_all_nodes()))} nodes")
print(f"Node coordinates: {len(service.get_all_node_coordinates())} nodes")
```

2. **Test LocationService:**
```python
from thong_tin.location_service import LocationService
from map.map_data_service import MapDataService
from thong_tin.models.location import Location

map_service = MapDataService()
location_service = LocationService(map_service=map_service)
location = Location(lat=21.0285, lng=105.8542)
nodes = location_service.addresses_to_nodes([location])
print(f"Node ID: {nodes[0]}")
```

3. **Test Solver:**
```python
from thuat_toan.solver import RouteSolver
from thong_tin.models.location import Location

solver = RouteSolver()
locations = [
    Location(lat=21.0285, lng=105.8542),
    Location(lat=21.0300, lng=105.8560)
]
result = solver.solve(locations)
print(f"Route: {result['route']}")
print(f"Distance: {result['distance']}")
print(f"Path coordinates: {len(result['path_coordinates'])} points")
```

## Kết luận

✅ **Đã kết nối:**
- Map data (OSM/sample) → MapDataService → Solver
- User coordinates → LocationService → Solver
- Solver → Algorithms (A*, GA) → Results
- Results → MapDataService → Path coordinates

✅ **Tất cả các module đã được kết nối và hoạt động cùng nhau!**

