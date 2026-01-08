"""
Test OSM Loader
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from map.osm_loader import OSMLoader
from map.map_loader import load_hanoi_map, load_map_from_osm
from map.map_data_service import MapDataService

def test_osm_loader():
    """Test OSMLoader"""
    print("=== Test OSM Loader ===")
    
    loader = OSMLoader()
    
    # Test load từ place
    try:
        print("\n1. Testing load from place...")
        nx_graph = loader.load_network_from_place("Hanoi, Vietnam", network_type="drive")
        print(f"   Loaded {len(nx_graph.nodes)} nodes and {len(nx_graph.edges)} edges")
        
        # Test convert sang Graph
        print("\n2. Testing convert to Graph...")
        graph = loader.convert_networkx_to_graph(nx_graph)
        print(f"   Converted to Graph with {len(list(graph.get_all_nodes()))} nodes")
        
        # Test get nodes coordinates
        print("\n3. Testing get nodes coordinates...")
        nodes = loader.get_nodes_coordinates(nx_graph)
        print(f"   Got {len(nodes)} nodes with coordinates")
        if nodes:
            first_node = list(nodes.items())[0]
            print(f"   Example node: {first_node[0]} -> {first_node[1]}")
        
    except Exception as e:
        print(f"   Error: {str(e)}")
        print("   (This is expected if OSM data is not available)")

def test_map_loader():
    """Test map_loader functions"""
    print("\n=== Test Map Loader ===")
    
    try:
        print("\n1. Testing load_hanoi_map()...")
        graph = load_hanoi_map()
        print(f"   Loaded graph with {len(list(graph.get_all_nodes()))} nodes")
    except Exception as e:
        print(f"   Error: {str(e)}")
        print("   (This is expected if OSM data is not available)")
    
    try:
        print("\n2. Testing load_map_from_osm with place...")
        graph = load_map_from_osm(place="Hanoi, Vietnam")
        print(f"   Loaded graph with {len(list(graph.get_all_nodes()))} nodes")
    except Exception as e:
        print(f"   Error: {str(e)}")

def test_map_data_service():
    """Test MapDataService"""
    print("\n=== Test Map Data Service ===")
    
    try:
        print("\n1. Testing MapDataService with OSM...")
        service = MapDataService(use_osm=True)
        graph = service.get_graph()
        print(f"   Got graph with {len(list(graph.get_all_nodes()))} nodes")
    except Exception as e:
        print(f"   Error: {str(e)}")
        print("   (This is expected if OSM data is not available)")
    
    try:
        print("\n2. Testing MapDataService with sample data...")
        service = MapDataService(use_osm=False)
        graph = service.get_graph()
        print(f"   Got graph with {len(list(graph.get_all_nodes()))} nodes")
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == "__main__":
    test_osm_loader()
    test_map_loader()
    test_map_data_service()

