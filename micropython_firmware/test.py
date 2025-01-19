data = b"ssid=Orange_Swiatlowod_E4C0_2.4GHz,password=5EvLo5Ux6rs9HGzjna"
start_byte = b'\x02'
end_byte = b'\x03'

# Maksymalny rozmiar danych w paczce
max_packet_size = 20

# Rozmiary danych w pierwszej i ostatniej paczce
max_data_first = max_packet_size - 1  # Zostawiamy miejsce na `start_byte`
max_data_last = max_packet_size - 1  # Zostawiamy miejsce na `end_byte`

# Dane do pierwszej paczki
first_packet_data = data[:max_data_first]
remaining_data = data[max_data_first:]

# Dane do ostatniej paczki
if len(remaining_data) > max_data_last:
    last_packet_data = remaining_data[-max_data_last:]
    middle_packets_data = remaining_data[:-max_data_last]
else:
    last_packet_data = remaining_data
    middle_packets_data = b""

# Podział danych na paczki pośrednie
middle_packets = [
    middle_packets_data[i : i + max_packet_size]
    for i in range(0, len(middle_packets_data), max_packet_size)
]

# Dodanie bajtów specjalnych
packets = [start_byte + first_packet_data]  # Pierwsza paczka
packets.extend(middle_packets)  # Paczki pośrednie
packets.append(last_packet_data + end_byte)  # Ostatnia paczka

# Konwersja do formatu HEX
packets_hex = [packet.hex() for packet in packets]
print(packets_hex)
