#/humidity_sensor
import random

def get_humidity():
    """Symulowany odczyt wilgotności"""
    return random.uniform(30.0, 90.0)  # Docelowo: odczyt z czujnika