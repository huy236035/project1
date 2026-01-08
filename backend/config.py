"""
Cấu hình ứng dụng
"""
import os

class Config:
    """
    Cấu hình chính
    """
    # Flask config
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Algorithm config
    GA_POPULATION_SIZE = int(os.getenv('GA_POPULATION_SIZE', 100))
    GA_GENERATIONS = int(os.getenv('GA_GENERATIONS', 500))
    GA_MUTATION_RATE = float(os.getenv('GA_MUTATION_RATE', 0.1))
    GA_ELITE_SIZE = int(os.getenv('GA_ELITE_SIZE', 5))
    
    # Map config
    CONSIDER_TRAFFIC = os.getenv('CONSIDER_TRAFFIC', 'True').lower() == 'true'
    USE_OSM = os.getenv('USE_OSM', 'True').lower() == 'true'
    OSM_PLACE = os.getenv('OSM_PLACE', 'Hanoi, Vietnam')
    OSM_NETWORK_TYPE = os.getenv('OSM_NETWORK_TYPE', 'drive')  # drive, walk, bike, all
    
    # API config
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

