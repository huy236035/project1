import requests
import logging

logger = logging.getLogger(__name__)

class OSRMService:
    """
    Service để tương tác với OSRM API
    """
    
    OSRM_BASE_URL = "http://router.project-osrm.org"
    
    @staticmethod
    def get_distance_matrix(coordinates):
        """
        Lấy ma trận khoảng cách từ OSRM
        
        Args:
            coordinates: List các dict {'lat': float, 'lng': float}
            
        Returns:
            List[List[float]]: Ma trận khoảng cách (mét)
            Nếu lỗi trả về None
        """
        if not coordinates:
            return None
            
        coords_str = ";".join([f"{p['lng']},{p['lat']}" for p in coordinates])
        
        url = f"{OSRMService.OSRM_BASE_URL}/table/v1/driving/{coords_str}?annotations=distance"
        
        try:
            logger.info(f"Calling OSRM API: {url}")
            response = requests.get(url, timeout=40)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 'Ok':
                    return data['distances']
                else:
                    logger.error(f"OSRM Error: {data.get('message')}")
            else:
                logger.error(f"OSRM Request Failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling OSRM: {str(e)}")
            
        return None
