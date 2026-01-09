# Luồng Chạy Chương Trình - Route Finder

Tài liệu này mô tả chi tiết luồng chạy của ứng dụng từ khi khởi động đến khi người dùng tìm đường đi.

## 📋 Mục Lục

1. [Khởi động Backend](#1-khởi-động-backend)
2. [Khởi động Frontend](#2-khởi-động-frontend)
3. [Luồng Người Dùng Chọn Điểm](#3-luồng-người-dùng-chọn-điểm)
4. [Luồng Tìm Đường Đi](#4-luồng-tìm-đường-đi)
5. [Luồng Hiển Thị Kết Quả](#5-luồng-hiển-thị-kết-quả)

---

## 1. Khởi động Backend

### 1.1. Entry Point
**File:** `backend/app.py`

```python
if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
```

**Chức năng:**
- Điểm vào chính của ứng dụng Flask
- Gọi `create_app()` để khởi tạo Flask app
- Chạy server trên port 5000 (mặc định)

### 1.2. Tạo Flask App
**File:** `backend/app.py` → `create_app()`

**Các bước:**
1. **Tạo Flask instance**
   ```python
   app = Flask(__name__)
   ```

2. **Cấu hình CORS**
   ```python
   CORS(app, origins=Config.CORS_ORIGINS)
   ```
   - Cho phép frontend (localhost:3000) gọi API
   - File cấu hình: `backend/config.py`

3. **Đăng ký Routes**
   ```python
   register_routes(app)
   ```
   - File: `backend/api/routes.py`
   - Đăng ký blueprint `route_bp` với prefix `/api`
   - Blueprint được định nghĩa trong `backend/api/route_api.py`

4. **Health Check Endpoint**
   ```python
   @app.route('/health', methods=['GET'])
   def health():
       return {'status': 'ok', 'service': 'route-finder'}, 200
   ```

**Kết quả:** Flask server chạy và sẵn sàng nhận request tại `http://localhost:5000`

---

## 2. Khởi động Frontend

### 2.1. Entry Point
**File:** `frontend/src/index.js`

```javascript
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**Chức năng:**
- Render React app vào DOM element `#root`
- Component gốc: `App`

### 2.2. Component App
**File:** `frontend/src/App.js`

```javascript
function App() {
  return (
    <div className="App">
      <h1>Bản đồ OpenStreetMap</h1>
      <Map />
    </div>
  );
}
```

**Chức năng:**
- Render component `Map` (component chính)

### 2.3. Component Map
**File:** `frontend/src/components/Map/Map.js`

**Khởi tạo:**
1. **State Management:**
   ```javascript
   const [selectedPoints, setSelectedPoints] = useState([]);
   const [routePath, setRoutePath] = useState([]);
   const [routeDistance, setRouteDistance] = useState(null);
   const [routeLegs, setRouteLegs] = useState([]);
   ```

2. **Kiểm tra Backend Connection:**
   ```javascript
   useEffect(() => {
     const checkBackendConnection = async () => {
       const isHealthy = await apiService.checkHealth();
       // ...
     };
     checkBackendConnection();
   }, []);
   ```
   - File service: `frontend/src/services/api.js`
   - Gọi `GET /health` để kiểm tra backend

3. **Render Map:**
   - Sử dụng `react-leaflet` để hiển thị bản đồ
   - Tile layer: OpenStreetMap
   - Center: Hà Nội (21.0285, 105.8542)

**Kết quả:** Frontend hiển thị bản đồ và sẵn sàng nhận tương tác từ người dùng

---

## 3. Luồng Người Dùng Chọn Điểm

### 3.1. User Click trên Map
**File:** `frontend/src/components/Map/Map.js`

**Component:** `MapClickHandler`
```javascript
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    },
  });
  return null;
}
```

**Chức năng:**
- Lắng nghe sự kiện click trên map
- Lấy tọa độ (lat, lng) từ event
- Gọi callback `onMapClick`

### 3.2. Xử Lý Click
**File:** `frontend/src/components/Map/Map.js` → `handleMapClick()`

**Các bước:**

1. **Tạo điểm mới:**
   ```javascript
   const newPoint = {
     id: Date.now() + Math.random(),
     lat: lat,
     lng: lng,
     number: prevPoints.length + 1,
     address: 'Đang tải địa chỉ...',
   };
   ```

2. **Reverse Geocoding:**
   ```javascript
   const address = await reverseGeocode(lat, lng);
   ```
   - Gọi OSM Nominatim API: `https://nominatim.openstreetmap.org/reverse`
   - Lấy địa chỉ từ tọa độ (số nhà, phố, phường, quận)
   - Cập nhật state với địa chỉ

3. **Cập nhật State:**
   ```javascript
   setSelectedPoints([...prevPoints, newPoint]);
   ```

4. **Render Marker:**
   - Tạo marker với icon tùy chỉnh (hình giọt nước)
   - Hiển thị số thứ tự trên marker
   - Hiển thị địa chỉ trong danh sách điểm

**Kết quả:** Marker xuất hiện trên map và điểm được thêm vào danh sách

---

## 4. Luồng Tìm Đường Đi

### 4.1. User Click "Tìm đường"
**File:** `frontend/src/components/Map/Map.js` → `handleFindRoute()`

**Điều kiện:** Phải có ít nhất 2 điểm đã chọn

### 4.2. Gửi Request đến Backend
**File:** `frontend/src/services/api.js` → `findMultiRoute()`

**Request:**
```javascript
POST http://localhost:5000/api/multi-route
{
  "points": [
    {"lat": 21.0285, "lng": 105.8542},
    {"lat": 21.0300, "lng": 105.8560},
    ...
  ],
  "consider_traffic": true,
  "ga_population_size": 100,
  "ga_generations": 500
}
```

### 4.3. Backend Nhận Request
**File:** `backend/api/route_api.py` → `find_multi_route()`

**Các bước:**

1. **Parse Request:**
   ```python
   data = request.get_json()
   points = data.get("points", [])
   ```

2. **Validate Dữ Liệu:**
   ```python
   is_valid, error_message = DataValidator.validate_coordinates(points)
   ```
   - File: `backend/thong_tin/data_validator.py`
   - Kiểm tra: tọa độ hợp lệ, có đủ điểm, ...

3. **Tạo Solver:**
   ```python
   solver = RouteSolver(consider_traffic=consider_traffic)
   ```
   - File: `backend/thuat_toan/solver.py`
   - Lazy load `MapDataService` (chỉ khi cần)

4. **Giải Bài Toán:**
   ```python
   result = solver.solve_from_coordinates(
       points,
       ga_population_size=ga_population_size,
       ga_generations=ga_generations
   )
   ```

### 4.4. Xử Lý trong Solver
**File:** `backend/thuat_toan/solver.py` → `solve_from_coordinates()`

**Các bước:**

1. **Tạo Graph đơn giản:**
   ```python
   graph = Graph()
   # Thêm edges giữa các điểm với khoảng cách Haversine
   ```

2. **Tính Ma Trận Khoảng Cách:**
   - Dùng Haversine distance giữa các cặp điểm
   - Lưu vào `distance_matrix`

3. **Genetic Algorithm (GA):**
   ```python
   best_route = genetic_algorithm(
       num_points=len(coordinates),
       distance_matrix=distance_matrix,
       population_size=ga_population_size,
       generations=ga_generations
   )
   ```
   - File: `backend/thuat_toan/algorithms/genetic_algorithm.py`
   - Tìm thứ tự tối ưu để đi qua tất cả điểm

4. **Trả về Kết quả:**
   ```python
   return {
       'route': best_route,  # [0, 2, 1, 3] - indices của điểm
       'distance': total_distance
   }
   ```

### 4.5. Backend Trả về Response
**File:** `backend/api/route_api.py` → `ResponseBuilder.multi_route_response()`

**Response:**
```json
{
  "success": true,
  "data": {
    "route": [0, 2, 1, 3],
    "distance": 24.90
  }
}
```

### 4.6. Frontend Nhận Response
**File:** `frontend/src/components/Map/Map.js` → `handleFindRoute()`

**Các bước:**

1. **Nhận Route Indices:**
   ```javascript
   const routeIndices = data.route; // [0, 2, 1, 3]
   ```

2. **Gọi OSM Routing API cho từng chặng:**
   ```javascript
   for (let i = 0; i < routeIndices.length - 1; i++) {
     const fromIdx = routeIndices[i];
     const toIdx = routeIndices[i + 1];
     
     // Gọi OSM Routing API
     const url = `https://routing.openstreetmap.de/routed-car/route/v1/driving/${lng1},${lat1};${lng2},${lat2}?overview=full&geometries=geojson`;
     const response = await fetch(url);
     const result = await response.json();
     
     // Lưu geometry và distance
     legs.push({ from, to, distance });
     allPaths.push(geometry);
   }
   ```

3. **Lưu Kết quả:**
   ```javascript
   setRoutePath(allPaths);
   setRouteDistance(totalDistance);
   setRouteLegs(legs);
   ```

**Kết quả:** Frontend có đầy đủ thông tin để vẽ đường đi chi tiết

---

## 5. Luồng Hiển Thị Kết Quả

### 5.1. Vẽ Đường Đi trên Map
**File:** `frontend/src/components/Map/Map.js`

**Render Polyline:**
```javascript
{routePath.length > 0 && routePath.map((path, idx) => (
  <Polyline
    key={`route-${idx}`}
    positions={path}
    color="#1a73e8"
    weight={5}
    opacity={0.9}
  />
))}
```

**Chức năng:**
- Vẽ từng chặng đi lên map
- Màu xanh đậm, độ dày 5px

### 5.2. Hiển Thị Thông Tin Chặng Đi
**File:** `frontend/src/components/Map/Map.js`

**Render Route Info:**
```javascript
{routeLegs.map((leg, index) => (
  <div key={index}>
    Chặng {index + 1} ({leg.from}-{leg.to}): {leg.distance.toFixed(2)} km
  </div>
))}
<div>
  Tổng: {routeDistance} km
</div>
```

**Ví dụ hiển thị:**
```
Chặng 1 (1-2): 8.81 km
Chặng 2 (2-4): 8.86 km
Chặng 3 (4-3): 7.23 km
─────────────────
Tổng: 24.90 km
```

### 5.3. Fit Map để Hiển Thị Toàn Bộ Route
**File:** `frontend/src/components/Map/Map.js`

```javascript
if (mapRef.current && allPaths.length > 0) {
  const allCoords = allPaths.flat();
  const bounds = L.latLngBounds(allCoords);
  mapRef.current.fitBounds(bounds, { padding: [50, 50] });
}
```

**Chức năng:**
- Tự động zoom và pan map để hiển thị toàn bộ route
- Padding 50px để không bị sát mép

---

## 📊 Sơ Đồ Luồng Tổng Quan

```
┌─────────────────┐
│  User Click Map │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  handleMapClick │
│  - Lấy tọa độ   │
│  - Reverse Geo  │
│  - Thêm marker  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Click "Tìm đường"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Frontend       │─────▶│  POST /api/      │
│  findMultiRoute │      │  multi-route     │
└─────────────────┘      └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  route_api.py    │
                          │  - Validate      │
                          │  - Tạo Solver    │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  solver.py       │
                          │  - Tạo Graph     │
                          │  - GA Algorithm  │
                          │  - Trả route    │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  Response        │
                          │  {route: [...]}  │
                          └────────┬─────────┘
                                   │
                                   ▼
┌─────────────────┐      ┌──────────────────┐
│  Frontend       │◀─────│  Nhận Response   │
│  - Gọi OSM API  │      │  - Route indices │
│  - Vẽ đường đi  │      └──────────────────┘
│  - Hiển thị info│
└─────────────────┘
```

---

## 🔑 Các File Quan Trọng

### Backend
- `backend/app.py` - Entry point, khởi tạo Flask app
- `backend/api/route_api.py` - API endpoints
- `backend/thuat_toan/solver.py` - Logic giải bài toán TSP
- `backend/thuat_toan/algorithms/genetic_algorithm.py` - GA algorithm
- `backend/thong_tin/data_validator.py` - Validate dữ liệu đầu vào

### Frontend
- `frontend/src/index.js` - Entry point React
- `frontend/src/App.js` - Component gốc
- `frontend/src/components/Map/Map.js` - Component bản đồ chính
- `frontend/src/services/api.js` - API service

---

## 📝 Ghi Chú

1. **Backend không cần osmnx**: Chỉ tính toán thứ tự tối ưu, không cần load OSM graph
2. **Frontend gọi OSM Routing API**: Lấy đường đi chi tiết và khoảng cách chính xác
3. **Lazy Loading**: `MapDataService` chỉ được khởi tạo khi cần (cho endpoint `/api/route`)
4. **Reverse Geocoding**: Tự động lấy địa chỉ khi user click trên map

