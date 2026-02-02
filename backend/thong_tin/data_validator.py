def validate_coordinates(points):
    if not points or not isinstance(points, list):
        return False, "Dữ liệu không hợp lệ: 'points' phải là một danh sách."
        
    if len(points) < 2:
        return False, "Cần ít nhất 2 điểm để tìm đường."
        
    for i, point in enumerate(points):
        if not isinstance(point, dict) or 'lat' not in point or 'lng' not in point:
            return False, f"Điểm thứ {i+1} không đúng định dạng."
            
        try:
            lat = float(point['lat'])
            lng = float(point['lng'])
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return False, f"Tọa độ điểm thứ {i+1} không hợp lệ."
        except ValueError:
            return False, f"Tọa độ điểm thứ {i+1} phải là số."
            
    return True, ""
