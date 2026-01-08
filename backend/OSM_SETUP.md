# Hướng dẫn cài đặt OSM dependencies

## Đã cài đặt thành công:
- ✅ networkx
- ✅ osmnx
- ✅ geopy
- ✅ requests
- ✅ shapely
- ✅ pandas
- ✅ numpy

## Còn thiếu (tùy chọn):
- ⚠️ geopandas (cần GDAL)

## Cài đặt geopandas (nếu cần):

### Trên Windows:
```bash
# Cách 1: Dùng conda (khuyến nghị)
conda install -c conda-forge osmnx

# Cách 2: Cài GDAL trước, sau đó cài geopandas
# Tải GDAL wheel từ: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
pip install GDAL-3.x.x-cp38-cp38-win_amd64.whl
pip install geopandas
```

### Trên Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev
pip install geopandas

# Mac
brew install gdal
pip install geopandas
```

## Lưu ý:
- Hệ thống đã được cấu hình để **KHÔNG dùng sample data**
- Nếu osmnx không hoạt động đầy đủ, hệ thống sẽ tạo graph đơn giản từ tọa độ người dùng
- Để có đường bộ chính xác, cần cài đặt đầy đủ osmnx + geopandas

## Test:
```python
python -c "import osmnx as ox; print('OSM OK')"
```


