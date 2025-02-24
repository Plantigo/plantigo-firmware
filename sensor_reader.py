import time
from dht22_sensor import get_dht22_data
from sht41_sensor import get_sht41_data
from soil_moisture_sensor import get_soil_moisture_data
from light_sensor import get_light


def read_all_sensors():
    sht41_data = get_sht41_data()

    if sht41_data["temperature"] is None or sht41_data["humidity"] is None:
        dht22_data = get_dht22_data()
        temperature = dht22_data["temperature"]
        humidity = dht22_data["humidity"]
    else:
        temperature = sht41_data["temperature"]
        humidity = sht41_data["humidity"]

    soil_data = get_soil_moisture_data()
    light = get_light()

    sensor_data = {
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_data["soil_moisture"],
        "pressure": light,
        "timestamp": time.time()
    }
    # print(sensor_data)
    return sensor_data
