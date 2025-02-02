#temperature_sensor
import random

def get_temperature():
    """Symulowany odczyt temperatury (docelowo: prawdziwy sensor)"""
    return random.uniform(15.0, 30.0)  # Docelowo: odczyt z czujnika