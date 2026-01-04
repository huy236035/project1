# Tìm đường ngắn nhất - Dijkstra

Ứng dụng web tìm đường ngắn nhất sử dụng thuật toán Dijkstra.

## Cấu trúc project

- **backend/**: Python Flask API server
  - `app.py`: Flask API server
  - `algorithms/dijkstra.py`: Thuật toán Dijkstra
  - `utils/graph.py`: Class Graph
- **src/**: React frontend
  - `App.js`: Component chính
  - `App.css`: Styling

## Cài đặt và chạy

### Backend (Python)

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Chạy server:
```bash
cd backend
python app.py
```

Server sẽ chạy tại: http://localhost:5000

### Frontend (React)

1. Cài đặt dependencies (nếu chưa có):
```bash
npm install
```

2. Chạy ứng dụng:
```bash
npm start
```

Ứng dụng sẽ mở tại: http://localhost:3000

## API Endpoints

- `GET /api/health`: Health check
- `GET /api/nodes`: Lấy danh sách tất cả nodes
- `POST /api/path`: Tìm đường đi ngắn nhất
  - Body: `{ "start": "A", "end": "F" }`
- `GET /api/graph`: Lấy toàn bộ đồ thị
- `POST /api/graph`: Tạo đồ thị mới từ edges

