# Hướng dẫn chạy Backend

## Cách 1: Chạy trực tiếp với `py`

```powershell
cd backend
py -3 app.py
```

## Cách 2: Sử dụng script

**Windows (PowerShell):**
```powershell
cd backend
.\run.ps1
```

**Windows (CMD):**
```cmd
cd backend
run.bat
```

## Cách 3: Chạy từ thư mục root

```powershell
py -3 backend/app.py
```

## Lưu ý

- Sử dụng `py -3` thay vì `python` để đảm bảo dùng Python 3
- Server sẽ chạy tại: `http://localhost:5000`
- Kiểm tra health: `http://localhost:5000/health`

## Troubleshooting

Nếu gặp lỗi import, đảm bảo:
1. Đã cài đặt dependencies: `pip install -r ../requirements.txt`
2. Đang ở đúng thư mục `backend/`
3. Sử dụng Python 3: `py -3`

