# Frontend - Route Finder

Frontend React application để tìm đường đi ngắn nhất qua nhiều điểm.

## Cài đặt

```bash
npm install
```

## Cấu hình

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env` nếu Backend chạy ở port khác:

```
REACT_APP_API_URL=http://localhost:5000
```

## Chạy ứng dụng

```bash
npm start
```

Ứng dụng sẽ chạy tại `http://localhost:3000`

## Cấu trúc

```
src/
├── components/
│   └── Map/
│       ├── Map.js          # Component bản đồ chính
│       └── Map.css         # Styles cho bản đồ
├── services/
│   └── api.js              # API service để gọi Backend
├── config/
│   └── api.js              # Cấu hình API
├── App.js                  # Component chính
└── index.js                # Entry point
```

## Tính năng

- ✅ Click trên bản đồ để chọn điểm
- ✅ Xóa điểm đã chọn
- ✅ Tìm đường đi tối ưu qua nhiều điểm
- ✅ Hiển thị route trên bản đồ
- ✅ Hiển thị khoảng cách
- ✅ Tự động fit map để hiển thị toàn bộ route
- ✅ Error handling và loading states

## API Endpoints

Frontend gọi các API sau từ Backend:

- `POST /api/multi-route` - Tìm route tối ưu qua nhiều điểm
- `GET /api/route?start=X&end=Y` - Tìm đường đi giữa 2 điểm
- `GET /health` - Kiểm tra health của Backend

## Sử dụng

1. **Chọn điểm**: Click trên bản đồ để chọn các điểm
2. **Tìm đường**: Click nút "Tìm đường" khi đã chọn ít nhất 2 điểm
3. **Xem kết quả**: Route sẽ được hiển thị trên bản đồ với khoảng cách

## Lưu ý

- Cần Backend chạy ở port 5000 (hoặc cấu hình trong `.env`)
- CORS đã được cấu hình trong Backend
- Nếu không kết nối được Backend, sẽ hiển thị thông báo lỗi

