# Backend - Route Finder

Backend API để tìm đường đi ngắn nhất qua nhiều điểm sử dụng thuật toán A* và Genetic Algorithm.

## Cấu trúc thư mục

```
backend/
├── api/                          # API Routes
│   ├── __init__.py
│   ├── routes.py                 # Đăng ký tất cả routes
│   └── route_api.py              # API tìm đường đi
│
├── thong_bao_trang_thai/         # Thông báo & Trạng thái
│   ├── __init__.py
│   ├── notification_service.py    # Service gửi thông báo
│   ├── status_service.py         # Service quản lý trạng thái
│   └── message_handler.py        # Xử lý các loại message
│
├── thong_tin/                    # Thông tin & Dữ liệu điểm
│   ├── __init__.py
│   ├── address_handler.py        # Xử lý địa chỉ các điểm
│   ├── location_service.py      # Service quản lý vị trí
│   ├── data_validator.py        # Validate dữ liệu đầu vào
│   └── models/
│       ├── __init__.py
│       ├── location.py           # Model địa điểm
│       └── address.py            # Model địa chỉ
│
├── map/                          # Xử lý bản đồ Hà Nội
│   ├── __init__.py
│   ├── map_loader.py            # Load dữ liệu bản đồ từ OSM/file
│   ├── traffic_handler.py       # Xử lý thông tin tắc đường
│   ├── road_network.py          # Quản lý mạng lưới đường
│   ├── map_data_service.py      # Service cung cấp dữ liệu bản đồ
│   └── data/
│       ├── __init__.py
│       ├── hanoi_nodes.py        # Dữ liệu nodes Hà Nội
│       └── traffic_data.py       # Dữ liệu tắc đường
│
├── thuat_toan/                   # Thuật toán
│   ├── __init__.py
│   ├── solver.py                # File Solver chính (kết hợp A* và GA)
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── astar.py             # Thuật toán A*
│   │   ├── genetic_algorithm.py # Thuật toán GA
│   │   └── dijkstra.py          # Thuật toán Dijkstra
│   └── utils/
│       ├── __init__.py
│       ├── graph.py             # Class Graph
│       ├── path_converter.py    # Chuyển đổi path sang coordinates
│       └── distance_calculator.py # Tính toán khoảng cách
│
├── ket_qua/                      # Kết quả & Response
│   ├── __init__.py
│   ├── result_formatter.py      # Format kết quả trả về
│   └── response_builder.py      # Xây dựng response JSON
│
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_astar.py
│   ├── test_genetic_algorithm.py
│   ├── test_multi_point.py
│   └── test_solver.py
│
├── utils/                        # Utilities chung
│   ├── __init__.py
│   ├── exceptions.py            # Custom exceptions
│   ├── logger.py                # Logging
│   └── helpers.py               # Helper functions
│
├── app.py                        # File chính khởi chạy Flask server
└── config.py                    # Cấu hình (database, API keys, etc.)
```

## Cách sử dụng

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi khi cài `osmnx`, có thể cần cài thêm:
```bash
pip install osmnx networkx geopy
```

### 2. Chạy server

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

### 3. API Endpoints

#### GET `/api/route`
Tìm đường đi giữa 2 điểm

**Query params:**
- `start`: Node ID điểm bắt đầu
- `end`: Node ID điểm kết thúc

**Ví dụ:**
```
GET /api/route?start=A&end=D
```

#### POST `/api/multi-route`
Tìm route tối ưu đi qua nhiều điểm từ tọa độ GPS

**Request body:**
```json
{
    "points": [
        {"lat": 21.0285, "lng": 105.8542},
        {"lat": 21.0300, "lng": 105.8560},
        {"lat": 21.0320, "lng": 105.8520}
    ],
    "consider_traffic": true,
    "ga_population_size": 100,
    "ga_generations": 500
}
```

**Response:**
```json
{
    "success": true,
    "route": ["A", "B", "C"],
    "distance": 15.5,
    "path_coordinates": [
        {"lat": 21.0285, "lng": 105.8542},
        ...
    ]
}
```

## Chạy tests

```bash
# Test A*
python -m tests.test_astar

# Test Genetic Algorithm
python -m tests.test_genetic_algorithm

# Test Multi-point
python -m tests.test_multi_point

# Test Solver
python -m tests.test_solver

# Test OSM Loader (cần internet)
python -m tests.test_osm_loader
```

## Mô tả các module

### `thuat_toan/`
Chứa các thuật toán tìm đường đi:
- **A***: Tìm đường đi ngắn nhất giữa 2 điểm
- **Genetic Algorithm**: Tối ưu thứ tự các điểm
- **Solver**: Kết hợp A* và GA để tìm đường đi tối ưu

### `map/`
Xử lý dữ liệu bản đồ Hà Nội từ OpenStreetMap (OSM):
- `osm_loader.py`: Load dữ liệu từ OSM (place, bbox, point)
- `map_loader.py`: Functions để load bản đồ từ OSM hoặc sample
- `map_data_service.py`: Service cung cấp dữ liệu bản đồ
- Xử lý thông tin tắc đường
- Quản lý mạng lưới đường
- Tự động fallback về sample data nếu không load được OSM

### `thong_tin/`
Xử lý thông tin và dữ liệu điểm:
- Validate dữ liệu đầu vào
- Chuyển đổi địa chỉ sang nodes
- Quản lý vị trí

### `thong_bao_trang_thai/`
Thông báo và quản lý trạng thái:
- Gửi thông báo cho người dùng
- Quản lý trạng thái request
- Xử lý các loại message

### `ket_qua/`
Format và xây dựng response:
- Format kết quả trả về
- Xây dựng response JSON

## Cấu hình

Các cấu hình có thể thay đổi trong `config.py` hoặc qua environment variables:

- `DEBUG`: Chế độ debug (default: True)
- `HOST`: Host để chạy server (default: 0.0.0.0)
- `PORT`: Port để chạy server (default: 5000)
- `GA_POPULATION_SIZE`: Số lượng cá thể trong GA (default: 100)
- `GA_GENERATIONS`: Số thế hệ trong GA (default: 500)
- `CONSIDER_TRAFFIC`: Có xem xét tắc đường không (default: True)

