"""
Test Solver chính
"""
from thuat_toan.solver import RouteSolver
from thong_tin.models.location import Location

def test_solver():
    """Test solver với nhiều điểm"""
    locations = [
        Location(lat=21.0285, lng=105.8542, name="Hồ Gươm"),
        Location(lat=21.0300, lng=105.8560, name="Điểm B"),
        Location(lat=21.0320, lng=105.8520, name="Điểm C"),
    ]
    
    solver = RouteSolver()
    result = solver.solve(locations)
    
    print("=== Test Solver ===")
    print(f"Route: {result['route']}")
    print(f"Distance: {result['distance']}")
    print(f"Path coordinates: {result['path_coordinates']}")
    
    return result

if __name__ == "__main__":
    test_solver()

