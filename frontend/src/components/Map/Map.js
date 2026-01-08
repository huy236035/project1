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

// Tạo custom icon với số thứ tự
function createNumberedIcon(number) {
  return L.divIcon({
    className: 'custom-numbered-marker',
    html: `<div class="marker-number">${number}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30],
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
  const [routeDistance, setRouteDistance] = useState(null); // Khoảng cách
  const [isCalculating, setIsCalculating] = useState(false); // Đang tính toán
  const [routeError, setRouteError] = useState(null); // Lỗi khi tính route
  const mapRef = useRef(null);

  // Xử lý khi click trên map
  const handleMapClick = useCallback((lat, lng) => {
    setSelectedPoints((prevPoints) => {
      const newPoint = {
        id: Date.now() + Math.random(), // ID unique dựa trên timestamp
        lat: lat,
        lng: lng,
        number: prevPoints.length + 1,
      };
      return [...prevPoints, newPoint];
    });
  }, []);

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
            
            // Chuyển đổi coordinates: [lng, lat] -> [lat, lng] cho Leaflet
            const geometry = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
            allPaths.push(geometry);
          } else {
            // Fallback: đường thẳng nếu không tìm thấy route
            allPaths.push([[fromPoint.lat, fromPoint.lng], [toPoint.lat, toPoint.lng]]);
          }
        } catch (err) {
          console.warn(`Error fetching route from OSM for segment ${i}:`, err);
          // Fallback: đường thẳng
          allPaths.push([[fromPoint.lat, fromPoint.lng], [toPoint.lat, toPoint.lng]]);
        }
      }
      
      // Bước 4: Lưu kết quả và vẽ lên map
      setRoutePath(allPaths); // Mảng các đường đi (mỗi phần tử là một Polyline)
      setRouteDistance(totalDistance.toFixed(2));

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
        {routeDistance !== null && (
          <div className="route-info">
            <strong>Khoảng cách: {routeDistance} km</strong>
          </div>
        )}
        {routeError && (
          <div className="route-error">
            {routeError}
          </div>
        )}
        <div className="points-list">
          {selectedPoints.length === 0 ? (
            <p className="empty-message">Chưa có điểm nào. Click trên bản đồ để chọn điểm.</p>
          ) : (
            selectedPoints.map((point) => (
              <div key={point.id} className="point-item">
                <span className="point-number">{point.number}</span>
                <span className="point-coords">
                  {point.lat.toFixed(6)}, {point.lng.toFixed(6)}
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
            color="#3498db"
            weight={4}
            opacity={0.7}
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
                <br />
                Lat: {point.lat.toFixed(6)}
                <br />
                Lng: {point.lng.toFixed(6)}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default Map;

