import json
from microdot import Microdot, Response
from temperature_sensor import get_temperature
from humidity_sensor import get_humidity
from pressure_sensor import get_pressure
from data_logger import data_logger
from data_compression import block_manager
from config_manager import config
import logging
import time
import os
import gc

logger = logging.getLogger("WebServer")

app = Microdot()

@app.route('/api/sensors')
def get_sensor_data(request):
    try:
        data = {
            "temperature": get_temperature(),
            "humidity": get_humidity(),
            "soil_moisture": get_pressure(),
            "timestamp": time.time()
        }
        
        # Zapisz dane do pliku
        data_logger.save_data(data)
        
        return Response(
            body=json.dumps(data),
            headers={"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Błąd podczas odczytu danych z czujników: {e}")
        return Response(
            body=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )

@app.route('/api/sensors/history')
def get_sensor_history(request):
    try:
        # Pobierz parametr hours z query string (domyślnie 24h)
        hours = int(request.args.get('hours', 24))
        
        # Pobierz historyczne dane
        data = data_logger.get_data(hours=hours)
        
        return Response(
            body=json.dumps(data),
            headers={"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Błąd podczas pobierania historycznych danych: {e}")
        return Response(
            body=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )

@app.route('/api/config', methods=['GET'])
def get_config(request):
    """Endpoint do pobierania aktualnej konfiguracji"""
    return Response(
        body=json.dumps(config.get_all()),
        headers={"Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"},
        status_code=200
    )

@app.route('/api/config', methods=['POST'])
def update_config(request):
    """Endpoint do aktualizacji konfiguracji"""
    try:
        new_config = json.loads(request.body)
        for section, values in new_config.items():
            for key, value in values.items():
                config.set(section, key, value)
        return Response(
            body=json.dumps({"status": "success"}),
            headers={"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"},
            status_code=200
        )
    except Exception as e:
        return Response(
            body=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
            status_code=400
        )

@app.route('/api/system')
def get_system_info(request):
    """Zwraca informacje o stanie systemu"""
    try:
        # Informacje o pamięci
        fs_stat = os.statvfs('/')
        flash_size = fs_stat[0] * fs_stat[2]  # całkowita wielkość
        flash_free = fs_stat[0] * fs_stat[3]  # wolne miejsce
        ram_free = gc.mem_free()
        ram_alloc = gc.mem_alloc()
        
        # Informacje o blokach danych
        block_count = len([f for f in os.listdir() if f.startswith(block_manager.filename_prefix)])
        
        # Aktualny interwał próbkowania
        current_hour = time.localtime().tm_hour
        day_start = config.get('data_storage', 'sampling_rate')['day_start_hour']
        day_end = config.get('data_storage', 'sampling_rate')['day_end_hour']
        current_interval = (
            config.get('data_storage', 'sampling_rate')['day_interval']
            if day_start <= current_hour < day_end
            else config.get('data_storage', 'sampling_rate')['night_interval']
        )
        
        system_info = {
            "memory": {
                "flash_total_kb": flash_size // 1024,
                "flash_free_kb": flash_free // 1024,
                "flash_used_percent": round((1 - flash_free/flash_size) * 100, 1),
                "ram_free_kb": ram_free // 1024,
                "ram_used_kb": ram_alloc // 1024,
                "ram_used_percent": round(ram_alloc/(ram_free + ram_alloc) * 100, 1)
            },
            "storage": {
                "block_count": block_count,
                "current_block_size": len(data_logger.current_block),
                "max_block_size": block_manager.compressor.BLOCK_SIZE
            },
            "sampling": {
                "current_interval": current_interval,
                "is_day_mode": day_start <= current_hour < day_end,
                "next_mode_change_hour": day_end if day_start <= current_hour < day_end else day_start
            }
        }
        
        return Response(
            body=json.dumps(system_info),
            headers={"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Błąd podczas pobierania informacji systemowych: {e}")
        return Response(
            body=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )

async def start_server():
    """Uruchamia serwer HTTP na porcie z konfiguracji"""
    port = config.get('web_server', 'port')
    debug = config.get('web_server', 'debug')
    logger.info(f"Uruchamianie serwera HTTP na porcie {port}...")
    app.run(port=port, debug=debug) 