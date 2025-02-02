#light_sensor
import random

def get_light():
    """Symulowany odczyt światła"""
    return random.randint(0, 1000)  # Docelowo: odczyt z czujnika