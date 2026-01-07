import { useState, useCallback, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
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
  }, [isDeleting]);

  return (
    <div className="map-container">
      <div className="points-panel">
        <div className="points-header">
          <h3>Điểm đã chọn ({selectedPoints.length})</h3>
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
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <MapClickHandler onMapClick={handleMapClick} />
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

