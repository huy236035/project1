import { useState, useCallback, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import apiService from '../../services/api';
import './Map.css';

// Fix icon issue với Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Component để xử lý click trên map
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    },
  });
  return null;
}

// Tạo icon marker 
function createNumberedIcon(number) {
  return L.divIcon({
    className: '',
    html: `
      <div class="gm-marker">
        <span>${number}</span>
      </div>
    `,
    iconSize: [30, 42],      // ⚠️ chiều cao lớn hơn để có không gian cho phần nhọn dài
    iconAnchor: [15, 42],    // mũi nhọn đúng tọa độ
    popupAnchor: [0, -36],
  });
}

function Map() {
  // Center mặc định: Hà Nội
  const center = [21.0285, 105.8542];
  const zoom = 13;
  
  // State để lưu danh sách các điểm đã chọn
  const [selectedPoints, setSelectedPoints] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [routePath, setRoutePath] = useState([]); // Đường đi từ backend
  const [routeDistance, setRouteDistance] = useState(null); // Khoảng cách tổng
  const [routeLegs, setRouteLegs] = useState([]); // Chi tiết từng chặng đi
  const [isCalculating, setIsCalculating] = useState(false); // Đang tính toán
  const [routeError, setRouteError] = useState(null); // Lỗi khi tính route
  const mapRef = useRef(null);

  // Hàm reverse geocoding để lấy địa chỉ từ tọa độ
  const reverseGeocode = useCallback(async (lat, lng) => {
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1&accept-language=vi`;
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'TSP Route Finder' // Nominatim yêu cầu User-Agent
        }
      });
      const data = await response.json();
      
      if (data && data.address) {
        const addr = data.address;
        const parts = [];
        
        // Số nhà
        if (addr.house_number) parts.push(addr.house_number);
        // Tên đường/phố
        if (addr.road || addr.street) parts.push(addr.road || addr.street);
        // Phường
        if (addr.suburb || addr.ward) parts.push(addr.suburb || addr.ward);
        // Quận/Huyện
        if (addr.city_district || addr.district) parts.push(addr.city_district || addr.district);
        // Quận (nếu có)
        if (addr.county && !addr.city_district) parts.push(addr.county);
        // Thành phố
        if (addr.city || addr.town) parts.push(addr.city || addr.town);
        
        if (parts.length > 0) {
          return parts.join(', ');
        }
      }
      
      return data.display_name || 'Không xác định được địa chỉ';
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      return 'Không xác định được địa chỉ';
    }
  }, []);

  // Xử lý khi click trên map
  const handleMapClick = useCallback(async (lat, lng) => {
    const newPointId = Date.now() + Math.random();
    
    // Thêm điểm với địa chỉ đang load
    setSelectedPoints((prevPoints) => {
      const newPoint = {
        id: newPointId,
        lat: lat,
        lng: lng,
        number: prevPoints.length + 1,
        address: 'Đang tải địa chỉ...',
      };
      return [...prevPoints, newPoint];
    });
    
    // Lấy địa chỉ
    const address = await reverseGeocode(lat, lng);
    
    // Cập nhật địa chỉ cho điểm vừa thêm
    setSelectedPoints((prevPoints) => 
      prevPoints.map(point => 
        point.id === newPointId 
          ? { ...point, address } 
          : point
      )
    );
  }, [reverseGeocode]);

  // Reset isDeleting flag sau khi state đã update
  useEffect(() => {
    if (isDeleting) {
      const timer = setTimeout(() => {
        setIsDeleting(false);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [isDeleting]);

  // Xóa một điểm - sử dụng functional update để tránh stale closure
  const handleRemovePoint = useCallback((id) => {
    if (isDeleting) return; // Tránh click liên tiếp
    
    setIsDeleting(true);
    setSelectedPoints((prevPoints) => {
      const updatedPoints = prevPoints
        .filter(point => point.id !== id)
        .map((point, index) => ({
          ...point,
          number: index + 1,
        }));
      return updatedPoints;
    });
  }, [isDeleting]);

  // Xóa tất cả điểm
  const handleClearAll = useCallback(() => {
    if (isDeleting) return; // Tránh click liên tiếp
    
    setIsDeleting(true);
    setSelectedPoints([]);
    setRoutePath([]);
    setRouteDistance(null);
    setRouteLegs([]);
    setRouteError(null);
  }, [isDeleting]);

  // Kiểm tra kết nối backend khi component mount
  useEffect(() => {
    const checkBackendConnection = async () => {
      const isHealthy = await apiService.checkHealth();
      if (!isHealthy) {
        setRouteError('Không thể kết nối đến Backend. Vui lòng kiểm tra server.');
      }
    };
    checkBackendConnection();
  }, []);

  // Tìm route tối ưu
  const handleFindRoute = useCallback(async () => {
    if (selectedPoints.length < 2) {
      setRouteError('Cần ít nhất 2 điểm để tìm đường');
      return;
    }

    setIsCalculating(true);
    setRouteError(null);
    setRoutePath([]);
    setRouteDistance(null);
    setRouteLegs([]);

    try {
      // Bước 1: Gửi request lên backend để tìm thứ tự tối ưu
      const data = await apiService.findMultiRoute(selectedPoints, {
        consider_traffic: true,
        ga_population_size: 100,
        ga_generations: 500
      });
      
      // Kiểm tra response format
      if (!data.route || data.route.length === 0) {
        throw new Error('Không tìm thấy đường đi');
      }
      
      // Bước 2: Nhận route indices từ backend (ví dụ: [0, 2, 1, 3])
      const routeIndices = data.route;
      
      // Bước 3: Gọi OSM Routing API cho từng cặp điểm liên tiếp
      const allPaths = []; // Mảng chứa các đường đi chi tiết
      const legs = []; // Mảng chứa thông tin từng chặng đi
      let totalDistance = 0;
      
      for (let i = 0; i < routeIndices.length - 1; i++) {
        const fromIdx = routeIndices[i];
        const toIdx = routeIndices[i + 1];
        const fromPoint = selectedPoints[fromIdx];
        const toPoint = selectedPoints[toIdx];
        
        if (!fromPoint || !toPoint) continue;
        
        try {
          // Gọi OSM Routing API
          const url = `https://routing.openstreetmap.de/routed-car/route/v1/driving/${fromPoint.lng},${fromPoint.lat};${toPoint.lng},${toPoint.lat}?overview=full&geometries=geojson`;
          const response = await fetch(url);
          const result = await response.json();
          
          if (result.routes && result.routes.length > 0) {
            const route = result.routes[0];
            const distanceKm = (route.distance / 1000).toFixed(2);
            totalDistance += parseFloat(distanceKm);
            
            // Lưu thông tin chặng đi
            legs.push({
              from: fromIdx + 1, // Số thứ tự điểm bắt đầu (1-indexed)
              to: toIdx + 1, // Số thứ tự điểm kết thúc (1-indexed)
              distance: parseFloat(distanceKm)
            });
            
            // Chuyển đổi coordinates: [lng, lat] -> [lat, lng] cho Leaflet
            const geometry = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
            allPaths.push(geometry);
          } else {
            // Fallback: đường thẳng nếu không tìm thấy route
            const fallbackDistance = parseFloat((Math.sqrt(
              Math.pow((toPoint.lat - fromPoint.lat) * 111, 2) + 
              Math.pow((toPoint.lng - fromPoint.lng) * 111 * Math.cos(fromPoint.lat * Math.PI / 180), 2)
            )).toFixed(2));
            totalDistance += fallbackDistance;
            legs.push({
              from: fromIdx + 1,
              to: toIdx + 1,
              distance: fallbackDistance
            });
            allPaths.push([[fromPoint.lat, fromPoint.lng], [toPoint.lat, toPoint.lng]]);
          }
        } catch (err) {
          console.warn(`Error fetching route from OSM for segment ${i}:`, err);
          // Fallback: đường thẳng
          const fallbackDistance = parseFloat((Math.sqrt(
            Math.pow((toPoint.lat - fromPoint.lat) * 111, 2) + 
            Math.pow((toPoint.lng - fromPoint.lng) * 111 * Math.cos(fromPoint.lat * Math.PI / 180), 2)
          )).toFixed(2));
          totalDistance += fallbackDistance;
          legs.push({
            from: fromIdx + 1,
            to: toIdx + 1,
            distance: fallbackDistance
          });
          allPaths.push([[fromPoint.lat, fromPoint.lng], [toPoint.lat, toPoint.lng]]);
        }
      }
      
      // Bước 4: Lưu kết quả và vẽ lên map
      setRoutePath(allPaths); // Mảng các đường đi (mỗi phần tử là một Polyline)
      setRouteDistance(totalDistance.toFixed(2));
      setRouteLegs(legs); // Lưu thông tin từng chặng đi

      // Fit map để hiển thị toàn bộ route
      if (mapRef.current && allPaths.length > 0) {
        // Tạo bounds từ tất cả các điểm trong route
        const allCoords = allPaths.flat();
        if (allCoords.length > 0) {
          const bounds = L.latLngBounds(allCoords);
          mapRef.current.fitBounds(bounds, { padding: [50, 50] });
        }
      }

    } catch (error) {
      console.error('Error finding route:', error);
      setRouteError(error.message || 'Có lỗi xảy ra khi tìm đường');
      setRoutePath([]);
      setRouteDistance(null);
      setRouteLegs([]);
    } finally {
      setIsCalculating(false);
    }
  }, [selectedPoints]);

  return (
    <div className="map-container">
      <div className="points-panel">
        <div className="points-header">
          <h3>Điểm đã chọn ({selectedPoints.length})</h3>
          <div className="header-buttons">
            {selectedPoints.length >= 2 && (
              <button 
                className="find-route-btn" 
                onClick={handleFindRoute}
                disabled={isCalculating || isDeleting}
              >
                {isCalculating ? (
                  <>
                    <span className="loading-spinner"></span>
                    Đang tính...
                  </>
                ) : (
                  'Tìm đường'
                )}
              </button>
            )}
            {selectedPoints.length > 0 && (
              <button 
                className="clear-btn" 
                onClick={handleClearAll}
                disabled={isDeleting}
              >
                {isDeleting ? 'Đang xóa...' : 'Xóa tất cả'}
              </button>
            )}
          </div>
        </div>
        {routeDistance !== null && routeLegs.length > 0 && (
          <div className="route-info">
            <div className="route-legs">
              {routeLegs.map((leg, index) => (
                <div key={index} className="route-leg-item">
                  Chặng {index + 1} ({leg.from}-{leg.to}): <strong>{leg.distance.toFixed(2)} km</strong>
                </div>
              ))}
            </div>
            <div className="route-total">
              <strong>Tổng: {routeDistance} km</strong>
            </div>
          </div>
        )}
        {routeError && (
          <div className="route-error">
            {routeError}
          </div>
        )}
        <div className="points-list">
          {selectedPoints.length === 0 ? (
            <div className="empty-message">
              <p>Chưa có điểm nào. Click trên bản đồ để chọn điểm.</p>
              <div style={{ marginTop: '10px', textAlign: 'left', fontSize: '12px', color: '#555' }}>
                <p><strong>Hướng dẫn sử dụng:</strong></p>
                <ol style={{ paddingLeft: '18px', margin: 0 }}>
                  <li>Click vào bản đồ để chọn các điểm cần đi qua (điểm 1, 2, 3,...).</li>
                  <li>Hệ thống sẽ luôn <strong>bắt đầu từ điểm 1</strong> và đi qua tất cả các điểm còn lại sao cho <strong>tổng quãng đường ngắn nhất</strong>.</li>
                  <li>Nhấn nút <strong>"Tìm đường"</strong> để hệ thống tính toán lộ trình tối ưu.</li>
                  <li>Quan sát đường đi màu xanh trên bản đồ và danh sách các chặng ở bên trái.</li>
                  <li>Nếu muốn làm lại, nhấn <strong>"Xóa tất cả"</strong> để chọn điểm mới.</li>
                </ol>
              </div>
            </div>
          ) : (
            selectedPoints.map((point) => (
              <div key={point.id} className="point-item">
                <span className="point-number">{point.number}</span>
                <span className="point-address">
                  {point.address || 'Đang tải địa chỉ...'}
                </span>
                <button 
                  className="remove-btn"
                  onClick={() => handleRemovePoint(point.id)}
                  title="Xóa điểm này"
                  disabled={isDeleting}
                >
                  ×
                </button>
              </div>
            ))
          )}
        </div>
      </div>
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
        whenCreated={(mapInstance) => {
          mapRef.current = mapInstance;
        }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <MapClickHandler onMapClick={handleMapClick} />
        {routePath.length > 0 && routePath.map((path, idx) => (
          <Polyline
            key={`route-${idx}`}
            positions={path}
            color="#1a73e8"
            weight={5}
            opacity={0.9}
          />
        ))}
        {selectedPoints.map((point) => (
          <Marker
            key={point.id}
            position={[point.lat, point.lng]}
            icon={createNumberedIcon(point.number)}
          >
            <Popup>
              <div>
                <strong>Điểm {point.number}</strong>
                {point.address && (
                  <>
                    <br />
                    {point.address}
                  </>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default Map;

