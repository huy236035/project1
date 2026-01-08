# Frontend-Backend Integration Guide

## Tổng quan

Frontend đã được cập nhật để kết nối với Backend API. Tài liệu này mô tả cách tích hợp hoạt động.

## Cấu trúc tích hợp

```
Frontend (React)
    ↓
API Service (services/api.js)
    ↓
Backend API (Flask)
    ↓
Route Solver
    ↓
Response
```

## API Endpoints

### 1. POST /api/multi-route

**Request:**
```json
{
  "points": [
    {"lat": 21.0285, "lng": 105.8542},
    {"lat": 21.0300, "lng": 105.8560}
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
  "route": ["123456", "789012"],
  "distance": 2.5,
  "path_coordinates": [
    {"lat": 21.0285, "lng": 105.8542},
    {"lat": 21.0300, "lng": 105.8560}
  ],
  "detailed_paths": {...}
}
```

### 2. GET /api/route?start=X&end=Y

**Response:**
```json
{
  "success": true,
  "data": {
    "distance": 2.5,
    "path": [
      {"lat": 21.0285, "lng": 105.8542},
      {"lat": 21.0300, "lng": 105.8560}
    ],
    "path_nodes": ["A", "B"]
  }
}
```

### 3. GET /health

**Response:**
```json
{
  "status": "ok",
  "service": "route-finder"
}
```

## Cách sử dụng trong Frontend

### 1. Import API Service

```javascript
import apiService from '../services/api';
```

### 2. Gọi API

```javascript
// Tìm route qua nhiều điểm
const result = await apiService.findMultiRoute(points, {
  consider_traffic: true,
  ga_population_size: 100,
  ga_generations: 500
});

// Sử dụng kết quả
const pathCoordinates = result.path_coordinates;
const distance = result.distance;
```

### 3. Error Handling

```javascript
try {
  const result = await apiService.findMultiRoute(points);
  // Xử lý kết quả
} catch (error) {
  // Xử lý lỗi
  console.error(error.message);
}
```

## Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục `frontend`:

```
REACT_APP_API_URL=http://localhost:5000
```

Nếu không có file `.env`, mặc định sẽ là `http://localhost:5000`.

### CORS

Backend đã được cấu hình CORS để cho phép Frontend gọi API. Kiểm tra trong `backend/app.py`:

```python
CORS(app, origins=Config.CORS_ORIGINS)
```

## Luồng hoạt động

1. **User chọn điểm trên map**
   - Frontend lưu tọa độ vào state

2. **User click "Tìm đường"**
   - Frontend gọi `apiService.findMultiRoute()`
   - API Service gửi POST request đến `/api/multi-route`

3. **Backend xử lý**
   - Validate dữ liệu
   - Tìm node gần nhất từ OSM/sample data
   - Tính toán route bằng A* và GA
   - Trả về kết quả

4. **Frontend nhận kết quả**
   - Hiển thị route trên map
   - Hiển thị khoảng cách
   - Fit map để hiển thị toàn bộ route

## Testing

### 1. Kiểm tra kết nối

```bash
# Chạy Backend
cd backend
python app.py

# Chạy Frontend
cd frontend
npm start
```

### 2. Test API

Mở browser console và test:

```javascript
// Test health check
const isHealthy = await apiService.checkHealth();
console.log('Backend healthy:', isHealthy);

// Test find route
const points = [
  {lat: 21.0285, lng: 105.8542},
  {lat: 21.0300, lng: 105.8560}
];
const result = await apiService.findMultiRoute(points);
console.log('Route result:', result);
```

## Troubleshooting

### Lỗi CORS

Nếu gặp lỗi CORS, kiểm tra:
- Backend có chạy không
- CORS_ORIGINS trong config có đúng không
- Frontend URL có được whitelist không

### Lỗi kết nối

- Kiểm tra Backend có chạy ở port 5000 không
- Kiểm tra `.env` file có đúng URL không
- Kiểm tra firewall/network

### Lỗi timeout

- Tăng `TIMEOUT` trong `config/api.js`
- Kiểm tra Backend có đang xử lý request không

## Best Practices

1. **Error Handling**: Luôn wrap API calls trong try-catch
2. **Loading States**: Hiển thị loading khi đang tính toán
3. **User Feedback**: Hiển thị thông báo lỗi rõ ràng
4. **Timeout**: Đặt timeout hợp lý cho requests
5. **Caching**: Có thể cache kết quả nếu cần

