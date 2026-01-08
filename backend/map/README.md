# Map Module - Xử lý dữ liệu bản đồ từ OSM

Module này xử lý việc load và quản lý dữ liệu bản đồ từ OpenStreetMap (OSM).

## Các file chính

### `osm_loader.py`
Class `OSMLoader` - Load dữ liệu từ OSM:
- `load_network_from_place()`: Load từ tên địa điểm
- `load_network_from_bbox()`: Load từ bounding box
- `load_network_from_point()`: Load từ một điểm trung tâm
- `convert_networkx_to_graph()`: Chuyển đổi NetworkX graph sang Graph object
- `get_nodes_coordinates()`: Lấy tọa độ các nodes
- `simplify_graph()`: Đơn giản hóa graph

### `map_loader.py`
Functions để load bản đồ:
- `load_map_from_sample()`: Load dữ liệu mẫu
- `load_map_from_osm()`: Load từ OSM với nhiều tùy chọn
- `load_hanoi_map()`: Load bản đồ Hà Nội từ OSM

### `map_data_service.py`
Class `MapDataService` - Service cung cấp dữ liệu bản đồ:
- Tự động load từ OSM hoặc sample data
- Quản lý traffic handler
- Áp dụng hệ số tắc đường vào graph

### `hanoi_nodes.py`
Quản lý nodes bản đồ Hà Nội:
- Có thể load từ OSM
- Fallback về sample data nếu không load được OSM

## Cách sử dụng

### Load bản đồ từ OSM

```python
from map.map_loader import load_hanoi_map

# Load bản đồ Hà Nội
graph = load_hanoi_map()
```

### Sử dụng MapDataService

```python
from map.map_data_service import MapDataService

# Khởi tạo với OSM
service = MapDataService(use_osm=True, place="Hanoi, Vietnam")

# Lấy graph
graph = service.get_graph(consider_traffic=True)
```

### Load từ nhiều nguồn khác nhau

```python
from map.map_loader import load_map_from_osm

# Load từ tên địa điểm
graph = load_map_from_osm(place="Hanoi, Vietnam")

# Load từ bounding box
bbox = (21.1, 20.9, 105.9, 105.7)  # (north, south, east, west)
graph = load_map_from_osm(bbox=bbox)

# Load từ điểm trung tâm
center = (21.0285, 105.8542)  # Hồ Gươm
graph = load_map_from_osm(center_point=center, dist=5000)
```

### Load nodes từ OSM

```python
from map.data.hanoi_nodes import load_nodes_from_osm, get_nodes

# Load nodes từ OSM
nodes = load_nodes_from_osm()

# Hoặc dùng function tự động
nodes = get_nodes(use_osm=True)
```

## Cấu hình

Có thể cấu hình qua environment variables:

```bash
USE_OSM=True                    # Có sử dụng OSM không
OSM_PLACE="Hanoi, Vietnam"      # Địa điểm để load
OSM_NETWORK_TYPE="drive"        # Loại mạng lưới (drive, walk, bike, all)
CONSIDER_TRAFFIC=True           # Có xem xét tắc đường không
```

## Lưu ý

1. **Lần đầu load OSM có thể mất thời gian** (vài phút) vì cần download dữ liệu
2. **OSM sử dụng cache** - lần sau sẽ nhanh hơn
3. **Nếu không có internet**, sẽ tự động fallback về sample data
4. **Network type**:
   - `drive`: Chỉ đường cho xe ô tô
   - `walk`: Đường đi bộ
   - `bike`: Đường cho xe đạp
   - `all`: Tất cả các loại đường

## Dependencies

- `osmnx`: Load dữ liệu từ OSM
- `networkx`: Xử lý graph
- `geopy`: Tính toán địa lý

